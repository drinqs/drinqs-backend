# imports
import pandas as pd

# Django imports
from django.core.cache import cache

# Surprise: https://surprise.readthedocs.io/en/stable/
from surprise import *

# Import Review model to get data from DB
from drinqsapp.models import Review


# Returns a surprise dataframe in the format needed
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
    reader = Reader(rating_scale=(-1, 1))
    data = Dataset.load_from_df(df[["user_id", "ctail_id", "rating"]], reader)
    return data


# Gets predictions from cache
def getModelAndPredictionsFromCacheOrDB():
    if cache.get('collaborativePredictions') is None:
        return setModelAndPredictionsInCache()
    else:
        return cache.get('collaborativePredictions')


# Sets the collaborative predictions to cache.
def setModelAndPredictionsInCache():
    dataset = formatData()
    trainset = dataset.build_full_trainset()
    algo = SVD(n_factors=19)
    # Fitting
    algo.fit(trainset)
    # Predict ratings for cocktails that are NOT in the training set.
    antiset = trainset.build_anti_testset()
    predset = algo.test(antiset)
    predAsFrame = pd.DataFrame()
    for uid, iid, r_ui, est, details in predset:
        predAsFrame.loc[uid, iid] = est
    cache.set(key='collaborativePredictions', value=predAsFrame, timeout=600)
    return cache.get('collaborativePredictions')


# Return predictions for a certain user
def getCollabRecsforUser(userId):
    '''Return the top  cocktail_id for a user,.i.e. userID
    Args:userId
    Returns: predictions vector
    '''
    # get predictions from Cache
    predictions = getModelAndPredictionsFromCacheOrDB()
    # First map the predictions to each user and drop the already rated cocktails (Na, since we used
    # the anti-testset)
    # if the user is not yet in the cached matrix, return Non = will receive only contest based until
    # matrix ist cached again
    try:
        predOfUser = predictions.loc[[userId]].dropna(axis=1)
    except:
        predOfUser = None
    return predOfUser


# Returns the already rated cocktails of a given user, inspired by https://www.jiristodulka.com/post/recsys_cf/
def histRatings(user_id):
    ctails = []
    for review in Review.objects.filter(user_id=user_id):
        ctails.append(review.cocktail_id)
    print('User {0} has already rated {1} movies.'.format(user_id, len(ctails)))
    return ctails
