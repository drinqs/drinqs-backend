from drinqsapp.models import Cocktail, CocktailCondensedMatrix, Review
import numpy as np
import pandas as pd
import scipy
import scipy.spatial
from django.core.cache import cache

def fetch_cocktail_similarity_matrix():
    similarity_matrix_from_cache = cache.get('cocktail_similarity_matrix')

    if similarity_matrix_from_cache is not None:
        return similarity_matrix_from_cache
    else:
        cocktail_similarity_matrix_from_db = scipy.spatial.distance.squareform(CocktailCondensedMatrix.objects.latest("id").value)
        np.fill_diagonal(cocktail_similarity_matrix_from_db, 1.0)

        cocktail_similarity_matrix = pd.DataFrame(
            data=cocktail_similarity_matrix_from_db[1:, 1:],
            index=cocktail_similarity_matrix_from_db[1:, 0],
            columns=cocktail_similarity_matrix_from_db[0, 1:],
        )
        cache.set(key='cocktail_similarity_matrix', value=cocktail_similarity_matrix, timeout=3600)

        return cocktail_similarity_matrix

def fetch_item_based_recommendations_for_user(user_id):
    '''
    Returns a vector with a length of the amount of all unrated cocktails with the sum of the
    weighted similarites of the already rated cocktails.
    The labels of the vector's values correspond to cocktail IDs\n
    The weight is determined by whether the already rated cocktails are liked,
    disliked, added or removed from bookmarks.
    '''

    item_based_recommendations = cache.get(f'item_based_recommendations-{user_id}')

    if item_based_recommendations is not None:
        return item_based_recommendations
    else:
        cocktail_similarity_matrix = fetch_cocktail_similarity_matrix()
        weighted_cocktail_similarities = []
        reviewed_cocktail_ids = []
        for review in Review.objects.filter(user_id=user_id):
            if review.liked == False:
                weight = -0.5
            elif review.bookmarked == True:
                weight = 1
            elif review.liked == True:
                weight = 0.5
            elif review.bookmarked == False:
                weight = -1

            weighted_cocktail_similarities_for_current_cocktail = cocktail_similarity_matrix.loc[[review.cocktail.id]] * weight

            weighted_cocktail_similarities.append(weighted_cocktail_similarities_for_current_cocktail)
            reviewed_cocktail_ids.append(review.cocktail_id)

        item_based_recommendations = pd.concat(weighted_cocktail_similarities)
        # drop columns for already reviewed IDs
        item_based_recommendations = item_based_recommendations.drop(labels=reviewed_cocktail_ids, axis=1)
        # compute sum of similarities of all unrated cocktails for each already rated cocktails
        item_based_recommendations = item_based_recommendations.sum().to_frame().transpose()
        cache.set(key=f'user_recommendation-{user_id}', value=item_based_recommendations, timeout=300)

        return item_based_recommendations

def update_cache_for_item_based_recommendations(user_id, review, old_review=None):
    '''
    Updates the weighted cocktail similarities vector (of item based recommendations)
    for the updated review's cocktail.
    '''

    cocktail_similarity_matrix = fetch_cocktail_similarity_matrix()
    item_based_recommendations = fetch_item_based_recommendations_for_user(user_id)

    if old_review is None:
        if review.liked == False:
            weight = -0.5
        elif review.bookmarked == True:
            weight = 1
        elif review.liked == True:
            weight = 0.5
        elif review.bookmarked == False:
            weight = -1

        weighted_cocktail_similarities = cocktail_similarity_matrix.loc[[review.cocktail.id]] * weight

        if weighted_cocktail_similarities.index[0] in item_based_recommendations.columns:
            difference = weighted_cocktail_similarities.columns.difference(item_based_recommendations.columns)
            weighted_cocktail_similarities = weighted_cocktail_similarities.drop(labels=difference, axis=1)

            item_based_recommendations = item_based_recommendations.append(weighted_cocktail_similarities)
            item_based_recommendations = item_based_recommendations.sum().to_frame().transpose()
            item_based_recommendations = item_based_recommendations.drop(labels=review.cocktail.id, axis=1)

            cache.set(key=f'user_recommendation-{user_id}', value=item_based_recommendations, timeout=180)
    else:
        if review.liked == False:
            new_review_weight = -0.5
        elif review.bookmarked == True:
            new_review_weight = 1
        elif review.liked == True:
            new_review_weight = 0.5
        elif review.bookmarked == False:
            new_review_weight = -1
        else:
            new_review_weight = 0

        if old_review.liked == False:
            old_review_weight = -0.5
        elif old_review.bookmarked == True:
            old_review_weight = 1
        elif old_review.liked == True:
            old_review_weight = 0.5
        elif old_review.bookmarked == False:
            old_review_weight = -1
        else:
            old_review_weight = 0

        weight_difference = new_review_weight - old_review_weight

        if not weight_difference == 0:
            weighted_cocktail_similarities = cocktail_similarity_matrix.loc[[review.cocktail.id]] * weight_difference
            difference = weighted_cocktail_similarities.columns.difference(item_based_recommendations.columns)
            weighted_cocktail_similarities = weighted_cocktail_similarities.drop(labels=difference, axis=1)
            currentUserProfile = currentUserProfile.append(weighted_cocktail_similarities)
            currentUserProfile = currentUserProfile.sum().to_frame().transpose()

            cache.set(key=f'user_recommendation_profile-{user_id}', value=currentUserProfile, timeout=300)
