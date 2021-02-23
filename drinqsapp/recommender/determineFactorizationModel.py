# imports
import pandas as pd
import time

# Surprise: https://surprise.readthedocs.io/en/stable/
from surprise import *
from surprise import Dataset, Reader, accuracy
from surprise.model_selection import *

# Own imports
from drinqsapp.models import Review


# Code inspired by
# https://towardsdatascience.com/building-and-testing-recommender-systems-with-surprise-step-by-step-d4ba702ef80b

# Returns a surprise dataframe in the format needed
def createSupriseDataframe():
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
    print(len(df))
    reader = Reader(rating_scale=(-1, 1))
    data = Dataset.load_from_df(df[["user_id", "ctail_id", "rating"]], reader)
    return data

# General comparision of performance of diff algorithms, cross_validate prints fitting time, prediction time and
# the RMSE
def compareAllAlgorithms(data):
    benchmark = []
    # Iterate over all algorithms
    for algorithm in [SVD(), SVDpp(), SlopeOne(), NMF(), NormalPredictor(), KNNBaseline(), KNNBasic(),
                      KNNWithMeans(), KNNWithZScore(), BaselineOnly(), CoClustering()]:
        # Perform cross validation
        results = cross_validate(algorithm, data, measures=['RMSE'], cv=5, verbose=False)
        # Get results & append algorithm name
        tmp = pd.DataFrame.from_dict(results).mean(axis=0)
        tmp = tmp.append(pd.Series([str(algorithm).split(' ')[0].split('.')[-1]], index=['Algorithm']))
        benchmark.append(tmp)
    benchmark = pd.DataFrame(benchmark).set_index('Algorithm').sort_values('test_rmse')
    print(benchmark)

# Based on results from compareAllAlgorithms, take a closer look
def compareBestAlgorithms(data):
    cross_validate(BaselineOnly(), data, measures=['RMSE'], cv=5, verbose=True)
    cross_validate(SVDpp(), data, measures=['RMSE', 'MAE'], cv=5, verbose=True)
    cross_validate(SVD(), data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

# SVD was chosen as a prediction algorithm generally tune it
def applyGridSearch(data):
    # Gridsearch
    param_grid = {'reg_all': [0.02, 0.002],
                  'lr_all': [0.0005, 0.005],
                  'n_epochs': [5, 20, 40, 50, 80, 77],
                  'n_factors': [19, 23, 39, 49]}
    gs = GridSearchCV(SVD, param_grid, measures=['rmse'], cv=5, refit=True)
    gs.fit(data)
    # best RMSE score
    print('best RMSE scor: ', gs.best_score['rmse'])
    print('best RMSE params: ', gs.best_params['rmse'])
    # combination of parameters that gave the best RMSE score
    algo = gs.best_estimator['rmse']
    cross_validate(algo, data, measures=['RMSE', 'MAE'], cv=5, verbose=True)

# check how good our predictions actually are
def checkwithTestset(data):
    trainset, testset = train_test_split(data, test_size=0.20)
    algo = SVD(n_factors=19)
    predictions = algo.fit(trainset).test(testset)
    print('general accuracy')
    accuracy.rmse(predictions)
    dump.dump('./dump_algo', algo)
    df = pd.DataFrame(predictions, columns=['uid', 'iid', 'rui', 'est', 'details'])
    df['err'] = abs(df.est - df.rui)
    best_predictions = df.sort_values(by='err')[:10]
    worst_predictions = df.sort_values(by='err')[-10:]
    print('best pred')
    print(best_predictions)
    print('worst pred')
    print(worst_predictions)
    median = df.sort_values(by='err').median(axis=0)
    print(median)





