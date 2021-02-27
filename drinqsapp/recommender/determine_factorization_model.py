# imports
import pandas as pd
import time

# Surprise: https://surprise.readthedocs.io/en/stable/
from surprise import *
from surprise import Dataset, Reader, accuracy
from surprise.model_selection import *

# Own imports
from drinqsapp.models import Review

AVAILABLE_ALGORITHMS = [
    SVD(), SVDpp(), SlopeOne(), NMF(), NormalPredictor(), KNNBaseline(), KNNBasic(),
    KNNWithMeans(), KNNWithZScore(), BaselineOnly(), CoClustering(),
]


# Code inspired by
# https://towardsdatascience.com/building-and-testing-recommender-systems-with-surprise-step-by-step-d4ba702ef80b


def create_review_dataset():
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
    data = Dataset.load_from_df(data_frame[["user_id", "cocktail_id", "rating"]], reader)

    return data


def compare_all_algorithms(data):
    """General comparision of performance of diff algorithms,
    `cross_validate` prints fitting time, prediction time and
    the RMSE.
    """

    benchmark = []

    # Iterate over all algorithms
    for algorithm in AVAILABLE_ALGORITHMS:
        # Perform cross validation
        results = cross_validate(algorithm, data, measures=['RMSE'], cv=5, verbose=False)
        # Get results & append algorithm name
        tmp = pd.DataFrame.from_dict(results).mean(axis=0)
        tmp = tmp.append(pd.Series([str(algorithm).split(' ')[0].split('.')[-1]], index=['Algorithm']))
        benchmark.append(tmp)

    benchmark = pd.DataFrame(benchmark).set_index('Algorithm').sort_values('test_rmse')
    print(benchmark)


def compare_best_algorithms(data):
    """
    Based on results from `compare_all_algorithms`, take a closer look
    """

    cross_validate(BaselineOnly(), data, measures=['RMSE'], cv=5, verbose=True)
    cross_validate(SVDpp(), data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
    cross_validate(SVD(), data, measures=['RMSE', 'MAE'], cv=5, verbose=True)


def apply_grid_search(data):
    """
    SVD was chosen as a prediction algorithm, generally tune it
    """
    # Further analysis see Jupyter Notebook "Matrix_Factorization_Notebook"
    # Gridsearch
    param_grid = {
        'reg_all': [0.02, 0.002],
        'lr_all': [0.0005, 0.005],
        'n_epochs': [5, 20, 40, 50, 80, 77],
        'n_factors': [19, 23, 39, 49],
    }

    grid_search = GridSearchCV(SVD, param_grid, measures=['rmse'], cv=5, refit=True)
    grid_search.fit(data)

    # best RMSE score
    print('best RMSE scor: ', grid_search.best_score['rmse'])
    print('best RMSE params: ', grid_search.best_params['rmse'])

    # combination of parameters that gave the best RMSE score
    algorithm = grid_search.best_estimator['rmse']
    cross_validate(algorithm, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)


# check how good our predictions actually are
def check_with_test_set(data):
    trainset, testset = train_test_split(data, test_size=0.20)
    algorithm = SVD(n_factors=19)
    predictions = algorithm.fit(trainset).test(testset)

    print('general accuracy')

    accuracy.rmse(predictions)
    dump.dump('./dump_algo', algorithm)
    data_frame = pd.DataFrame(predictions, columns=['uid', 'iid', 'rui', 'est', 'details'])
    data_frame['err'] = abs(data_frame.est - data_frame.rui)
    best_predictions = data_frame.sort_values(by='err')[:10]
    worst_predictions = data_frame.sort_values(by='err')[-10:]

    print('best pred')
    print(best_predictions)
    print('worst pred')
    print(worst_predictions)

    median = data_frame.sort_values(by='err').median(axis=0)
    print(median)
