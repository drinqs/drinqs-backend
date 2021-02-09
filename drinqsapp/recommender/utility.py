from drinqsapp.models import Cocktail, CocktailCondensedMatrix, Review
import numpy as np
import pandas as pd
import scipy
import scipy.spatial
from django.db.models import Case, When
from django.core.cache import cache
from drinqsapp.recommender import collaborativeUtility
from sklearn.preprocessing import Normalizer, MinMaxScaler

import time
import asyncio

# TODO: implement serverside caching of distanceMatrix
def getCocktailSimilarityFromCacheOrDB():
    if cache.get('cocktailSimilarity') is None:
        MatrixFromDB = CocktailCondensedMatrix.objects.latest("id")
        squaredMatrixFromDB = scipy.spatial.distance.squareform(MatrixFromDB.value)
        np.fill_diagonal(squaredMatrixFromDB, 1.0)
        result = pd.DataFrame(data=squaredMatrixFromDB[1:, 1:],
                            index=squaredMatrixFromDB[1:, 0],
                            columns=squaredMatrixFromDB[0, 1:])
        cache.set(key='cocktailSimilarity', value=result, timeout=3600)
        return result
    else:
        return cache.get('cocktailSimilarity')



def getUserProfileOnCocktailSimilaritiesFromCacheOrDB(userID):
    if cache.get('user_rec' + str(userID)) is None:
        cocktailDistanceDataFrame = getCocktailSimilarityFromCacheOrDB()
        list = []
        cocktailIdsWithReview = []
        for review in Review.objects.filter(user_id=userID):
            if review.liked == False:
                curRow = cocktailDistanceDataFrame.loc[[review.cocktail.id]] * -0.5
            elif review.bookmarked == True:
                curRow = cocktailDistanceDataFrame.loc[[review.cocktail.id]] * 1
            elif review.liked == True:
                curRow = cocktailDistanceDataFrame.loc[[review.cocktail.id]] * 0.5
            elif review.bookmarked == False:
                curRow = cocktailDistanceDataFrame.loc[[review.cocktail.id]] * -1

            list.append(curRow)
            cocktailIdsWithReview.append(review.cocktail_id)
        profile = pd.concat(list)
        profile = profile.drop(labels=cocktailIdsWithReview, axis=1)
        profile_sum =profile.sum().to_frame().transpose()
        cache.set(key='user_rec' + str(userID), value=profile_sum, timeout=300)
        return profile_sum
    else:
        return cache.get('user_rec' + str(userID))


def getRecommendationForUser(userID, getOnlyFirst):
    #start = time.time()
    collaborativeRecs = collaborativeUtility.getCollabRecsforUser(userID)
    itemBasedRecs = getUserProfileOnCocktailSimilaritiesFromCacheOrDB(userID)
    #print(time.time() - start)

    scaler1 = MinMaxScaler(feature_range=(0, 1)).fit(itemBasedRecs.T)
    scaler2 = MinMaxScaler(feature_range=(0, 1)).fit(collaborativeRecs.T)

    itemBasedRecs.iloc[:,:] = scaler1.transform(itemBasedRecs.T).T

    collaborativeRecs.iloc[:,:] = scaler2.transform(collaborativeRecs.T).T

    #print(time.time() - start)

    reviewCount = Review.objects.filter(user_id=userID).count()

    weightCollaborative = (min((reviewCount / 180), 0.6))

    bothRecsInFrame = itemBasedRecs.append(collaborativeRecs)
    itemBasedRecs.index = [userID]
    bothRecsInFrame.fillna(value=itemBasedRecs, axis=1, inplace=True)
    bothRecsInFrameWeightened = bothRecsInFrame.mul([1-weightCollaborative, weightCollaborative], axis=0)

    combinedRecommendations = bothRecsInFrameWeightened.sum().to_frame().transpose()
    combinedRecommendations = combinedRecommendations.sort_values(by=0, axis=1, ascending=False)
    #print(time.time() - start)

    if getOnlyFirst:
        lastRec = cache.get('last_user_rec' + str(userID))
        if lastRec is None:
            cocktail = Cocktail.objects.get(pk=combinedRecommendations.columns[0])
        else:
            if combinedRecommendations.columns[0] == lastRec:
                cocktail = Cocktail.objects.get(pk=combinedRecommendations.columns[1])
            else:
                cocktail = Cocktail.objects.get(pk=combinedRecommendations.columns[0])
        return cocktail
    else:
        intListOfIndices = combinedRecommendations.columns.astype(int)
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(intListOfIndices)])
        cocktails = Cocktail.objects.filter(pk__in=intListOfIndices).order_by(preserved)
    return cocktails


def updateCachedUserRecOnMutate(userID, updatedReview, oldReview=None):
    cocktailDistanceDataFrame = getCocktailSimilarityFromCacheOrDB()
    currentUserProfile = getUserProfileOnCocktailSimilaritiesFromCacheOrDB(userID)

    if oldReview is None:
        if updatedReview.liked == False:
            curRow = cocktailDistanceDataFrame.loc[[updatedReview.cocktail.id]] * -0.5
        elif updatedReview.bookmarked == True:
            curRow = cocktailDistanceDataFrame.loc[[updatedReview.cocktail.id]] * 1
        elif updatedReview.liked == True:
            curRow = cocktailDistanceDataFrame.loc[[updatedReview.cocktail.id]] * 0.5
        elif updatedReview.bookmarked == False:
            curRow = cocktailDistanceDataFrame.loc[[updatedReview.cocktail.id]] * -1

        if curRow.index[0] in currentUserProfile.columns:
            difference = curRow.columns.difference(currentUserProfile.columns)
            curRow = curRow.drop(labels=difference, axis=1)
            currentUserProfile = currentUserProfile.append(curRow)
            currentUserProfile = currentUserProfile.sum().to_frame().transpose()
            currentUserProfile = currentUserProfile.drop(labels=updatedReview.cocktail.id, axis=1)
            cache.set(key='user_rec' + str(userID), value=currentUserProfile, timeout=180)
    else:

        if updatedReview.liked == False:
            weightUpdatedRev = -0.5
        elif updatedReview.bookmarked == True:
            weightUpdatedRev = 1
        elif updatedReview.liked == True:
            weightUpdatedRev = 0.5
        elif updatedReview.bookmarked == False:
            weightUpdatedRev = -1
        else:
            weightUpdatedRev = 0

        if oldReview.liked == False:
            weightOldRev = -0.5
        elif oldReview.bookmarked == True:
            weightOldRev = 1
        elif oldReview.liked == True:
            weightOldRev = 0.5
        elif oldReview.bookmarked == False:
            weightOldRev = -1
        else:
            weightOldRev = 0

        weightDiff = weightUpdatedRev - weightOldRev
        if not weightDiff == 0:
            curRow = cocktailDistanceDataFrame.loc[[updatedReview.cocktail.id]] * weightDiff
            difference = curRow.columns.difference(currentUserProfile.columns)
            curRow = curRow.drop(labels=difference, axis=1)
            currentUserProfile = currentUserProfile.append(curRow)
            currentUserProfile = currentUserProfile.sum().to_frame().transpose()
            cache.set(key='user_rec' + str(userID), value=currentUserProfile, timeout=300)
