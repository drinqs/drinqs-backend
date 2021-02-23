from .collaborative_filtering import fetch_collaborative_recommendations_for_user
from .contentbased_filtering import fetch_item_based_recommendations_for_user
from django.core.cache import cache
from drinqsapp.models import Review, Cocktail
from sklearn.preprocessing import Normalizer, MinMaxScaler

def fetch_user_recommendations(user_id, only_first=False):
    collaborative_recommendations = fetch_collaborative_recommendations_for_user(user_id)
    item_based_recommendations = fetch_item_based_recommendations_for_user(user_id)

    if collaborative_recommendations is not None:
        transposed_item_based_recommendations = item_based_recommendations.T
        transposed_collaborative_recommendations = collaborative_recommendations.T

        # fit values in range between 0 and 1 to make them unifiable
        item_based_scaler = MinMaxScaler(feature_range=(0, 1)).fit(transposed_item_based_recommendations)
        collaborative_filtering_scaler = MinMaxScaler(feature_range=(0, 1)).fit(transposed_collaborative_recommendations)

        item_based_recommendations.iloc[:,:] = item_based_scaler.transform(transposed_item_based_recommendations).T
        collaborative_recommendations.iloc[:,:] = collaborative_filtering_scaler.transform(transposed_collaborative_recommendations).T

        review_count = Review.objects.filter(user_id=user_id).count()
        weight_for_collaborative_filtering = (min((review_count / 180), 0.6))

        unified_recommendations = item_based_recommendations.append(collaborative_recommendations)
        item_based_recommendations.index = [user_id]
        unified_recommendations.fillna(value=item_based_recommendations, axis=1, inplace=True)
        unified_recommendations = unified_recommendations.mul(
            [1 - weight_for_collaborative_filtering, weight_for_collaborative_filtering],
            axis=0,
        )
        recommendations = unified_recommendations.sum().to_frame().transpose()
    else:
        recommendations = item_based_recommendations

    recommendations = recommendations.sort_values(by=0, axis=1, ascending=False)

    if only_first:
        last_recommendation = cache.get(f'last_user_recommendation-{user_id}')
        if last_recommendation is None:
            cocktail = Cocktail.objects.get(pk=recommendations.columns[0])
        else:
            if recommendations.columns[0] == last_recommendation:
                cocktail = Cocktail.objects.get(pk=recommendations.columns[1])
            else:
                cocktail = Cocktail.objects.get(pk=recommendations.columns[0])
        return cocktail
    else:
        ranks_dataframe = recommendations.transpose()
        ranks_dataframe.insert(loc=0, column='cocktail_id', value=recommendations.columns.astype(int))
        # array of tuples in the manner [(cocktail_id, priority), ...]
        ranks = list(ranks_dataframe.itertuples(index=False, name=None))

        return Cocktail.objects.raw(
            '''
                SELECT *
                FROM drinqsapp_cocktail
                JOIN (VALUES %(ranks)s) AS ranks (cocktail_id, rank)
                    ON drinqsapp_cocktail.id = ranks.cocktail_id
                WHERE drinqsapp_cocktail.id IN %%(cocktail_ids)s
                ORDER BY ranks.rank DESC
            ''' % { 'ranks': ', '.join(map(lambda x: str(x), ranks)) },
            { 'cocktail_ids': tuple(recommendations.columns.astype(int)) },
        )
