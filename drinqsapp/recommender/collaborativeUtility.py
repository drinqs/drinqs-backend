# imports
import numpy as np
import pandas as pd
import time
from drinqsapp.recommender import utility

from django.db.models import Case, When
from django.core.cache import cache

# Surprise: https://surprise.readthedocs.io/en/stable/
import surprise
from pandas._libs.internals import defaultdict
from surprise.reader import Reader
from surprise import Dataset
from surprise.model_selection import GridSearchCV

  ##CrossValidation
from surprise.model_selection import cross_validate

  ##Matrix Factorization Algorithms
from surprise import *

from drinqsapp.models import Review, Cocktail

from abc import ABC
from django.core.management.base import BaseCommand

def formatData():
    df = pd.DataFrame(columns=["user_id", "ctail_id", "rating"])
    for review in Review.objects.all():

        if not review.liked:
            df.loc[review.id] = [review.user_id, review.cocktail_id, -0.5]
        elif review.bookmarked:
            df.loc[review.id] = [review.user_id, review.cocktail_id, 1]
        elif review.liked:
            df.loc[review.id] = [review.user_id, review.cocktail_id, 0.5]
        elif not review.bookmarked:
            df.loc[review.id] = [review.user_id, review.cocktail_id, -1]


    return df


def getModelAndPredictionsFromCacheOrDB():
    if cache.get('collaborativePredictions') is None:
        return setModelAndPredictionsInCache()
    else:
        return cache.get('collaborativePredictions')


# Sets the collaborative predictions to cache, can be used for updates, too.
def setModelAndPredictionsInCache():
        #start = time.time()
        df = formatData()
        #formated = time.time()-start
        #start = time.time()
        #print('data formatting:', formated)
        reader = Reader(rating_scale=(-1, 1))
        data = Dataset.load_from_df(df[["user_id", "ctail_id", "rating"]], reader)
        trainset = data.build_full_trainset()
        # Testset to verify results with trainset
        testset = trainset.build_testset()
       # built = time.time() - start
        #start = time.time()
        #print('data sets built:', built)
        algo = SVD(n_epochs=10, n_factors=15)
        # Fitting
        algo.fit(trainset)
        # Predict ratings for all pairs (i,j) that are NOT in the training set.
        predset1 = trainset.build_anti_testset()
        predset = algo.test(predset1)
        #predict = time.time() - start
        #start = time.time()
        #print('data prediction:', predict)
        predAsFrame = pd.DataFrame()
        for uid, iid, r_ui, est, details in predset:
            predAsFrame.loc[uid, iid] = est

        cache.set(key='collaborativePredictions', value=predAsFrame, timeout=600)
        #setcache = time.time() - start
        #start = time.time()
        #print('data setcache:', setcache)
        # ist das hier nach set noch nötig?
        return cache.get('collaborativePredictions')


# N is optional, return all prediction for a certain user without n
def getCollabRecsforUser(userId):
    '''Return the top N (default) cocktail_id for a user,.i.e. userID
    Args:userId, n= None
    Returns: return predictions vector

    '''
    # get predictions from Cache
    start = time.time()
    predictions = getModelAndPredictionsFromCacheOrDB()

    # First map the predictions to each user.
    #start = time.time()
    try:
        predOfUser = predictions.loc[[userId]].dropna(axis=1)
    except:
        predOfUser = None

    #top_n = defaultdict(list)
    #for uid, iid, r_ui, est, details in predictions:
    #    if uid == userId:
    #         top_n[uid].append((iid, est))

    #print(top_n)

    # Then sort the predictions for each user and retrieve the k highest ones.
    #start = time.time()
    #for uid, user_ratings in top_n.items():
    #    print(type(user_ratings))
    #    user_ratings.sort(key=lambda x: x[1], reverse=True)
    #    if n is not None:
    #        top_n[uid] = user_ratings[: n]
    #    else:
    #        top_n[uid] = user_ratings

    # Part II.: inspired by: https://beckernick.github.io/matrix-factorization-recommender/
    #start = time.time()
    # Data Frame with predictions.
    #preds_df = pd.DataFrame()

    #for id, row in top_n.items():
    #    test = pd.DataFrame(row, index=2)
    #    print("asd")
        #for pair in row:
        #    preds_df.loc[id, pair[0]] = pair[1]
    return predOfUser

# Returns the already rated cocktails of a given user
def histRatings(user_id):
    ctails = []
    for review in Review.objects.filter(user_id=user_id):
        ctails.append(review.cocktail_id)
    print('User {0} has already rated {1} movies.'.format(user_id, len(ctails)))
    return ctails


def getColabRecsForUser2(userID, getOnlyFirst):
    if getOnlyFirst:
        user_based_recs = get_top_n_for_user(userID, n=1)
        cocktail = Cocktail.objects.get(pk=user_based_recs.columns[0])
        return cocktail

    else:
        user_based_pred = get_top_n_for_user(userID)
        intListOfIndices = list(user_based_pred.columns)
        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(intListOfIndices)])
        cocktails = Cocktail.objects.filter(pk__in=intListOfIndices).order_by(preserved)
        return cocktails









