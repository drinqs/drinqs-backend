# imports
import pandas as pd

# Django imports
from django.core.cache import cache
from django.db.models import Subquery

# Surprise: https://surprise.readthedocs.io/en/stable/
from surprise import *

# Own imports
from drinqsapp.models import Review, User, Cocktail



def fetch_review_dataset():
    """
    Returns a surprise `Dataset` containing user_id, cocktail_id,
    and rating for each review in the database.
    """

    data_frame = pd.DataFrame(columns=["user_id", "cocktail_id", "rating"])

    for review in Review.objects.all():
        if not review.liked:
            data_frame.loc[review.id] = [review.user_id, review.cocktail_id, -0.5]
        elif review.bookmarked:
            data_frame.loc[review.id] = [review.user_id, review.cocktail_id, 1]
        elif review.liked:
            data_frame.loc[review.id] = [review.user_id, review.cocktail_id, 0.5]
        elif not review.bookmarked:
            data_frame.loc[review.id] = [review.user_id, review.cocktail_id, -1]

    reader = Reader(rating_scale=(-1, 1))

    return Dataset.load_from_df(data_frame[["user_id", "cocktail_id", "rating"]], reader)


# Gets recommendations from cache
def fetch_collaborative_recommendations():
    collaborative_recommendations = cache.get('collaborative_recommendations')
    if collaborative_recommendations is not None:
        return collaborative_recommendations
    else:
        return set_collaborative_recommendations()


# Sets the collaborative recommendations to cache.
def set_collaborative_recommendations():
    review_dataset = fetch_review_dataset()
    trainset = review_dataset.build_full_trainset()

    algorithm = SVD(n_factors=19)
    # Fitting
    algorithm.fit(trainset)
    # Predict ratings for cocktails that are NOT in the training set.
    anti_set = trainset.build_anti_testset()
    recommendation_set = algorithm.test(anti_set)
    recommendations_data_frame = pd.DataFrame()
    for user_id, cocktail_id, true_rating, estimated_rating, details in recommendation_set:
        recommendations_data_frame.loc[user_id, cocktail_id] = estimated_rating

    cache.set(key='collaborative_recommendations', value=recommendations_data_frame, timeout=600)

    return recommendations_data_frame


# Return recommendations for a certain user
def fetch_collaborative_recommendations_for_user(user_id):
    """Return the top cocktails for a user based on the rating of other users."""

    recommendations = fetch_collaborative_recommendations()

    try:
        return recommendations.loc[[user_id]].dropna(axis=1)
    except TypeError:
        return None


def rating_history(username):
    """
    Returns the already rated cocktails of a given user, inspired by https://www.jiristodulka.com/post/recsys_cf/
    """

    user = User.objects.get(username=username)
    print(f'User <{user.username}> has already rated {user.review_set.count()} movies.')

    return Cocktail.objects.filter(id__in=Subquery(user.review_set.values_list('cocktail_id', flat=True)))
