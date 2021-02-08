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
    start = time.time()
    collaborativeRecs = collaborativeUtility.getCollabRecsforUser(userID)
    itemBasedRecs = getUserProfileOnCocktailSimilaritiesFromCacheOrDB(userID)
    print(time.time() - start)

    scaler1 = MinMaxScaler(feature_range=(0, 1)).fit(itemBasedRecs.T)
    scaler2 = MinMaxScaler(feature_range=(0, 1)).fit(collaborativeRecs.T)

    print(collaborativeRecs.sort_values(by=userID, axis=1, ascending=False))
    print(itemBasedRecs.sort_values(by=0, axis=1, ascending=False))
    print("----------------------------")

    print("sorted itemBasedRecs scaled ")
    itemBasedRecs.iloc[:,:] = scaler1.transform(itemBasedRecs.T).T
    print(itemBasedRecs.sort_values(by=0, axis=1, ascending=False))

    print("collaborativeRecs scaled ")
    collaborativeRecs.iloc[:,:] = scaler2.transform(collaborativeRecs.T).T
    print(collaborativeRecs.sort_values(by=userID, axis=1, ascending=False))

    print(time.time() - start)

    weightCollaborative = ( min (numberOfRatingsOFUserX) / 220 ; 0,6)
    collaborativeRecs= collaborativeRecs * weightCollaborative
    itemBasedRecs = itemBasedRecs * 1 - weightCollaborative

    appendedStuff = itemBasedRecs.append(collaborativeRecs)
    print(appendedStuff)
    test = appendedStuff.sum().to_frame().transpose()
    print(test)
    print(time.time() - start)
    #    .sort_values(by=0, axis=1, ascending=False)
    #if getOnlyFirst:
    #    cocktail = Cocktail.objects.get(pk=itemBasedRecommendations.columns[0])
    #    return cocktail
    #else:
    #    intListOfIndices = itemBasedRecommendations.columns.astype(int)
     #   preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(intListOfIndices)])
    #    cocktails = Cocktail.objects.filter(pk__in=intListOfIndices).order_by(preserved)
    #return cocktails
    return None


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


