from drinqsapp.models import CocktailCondensedMatrix, Review
import numpy as np
import pandas as pd
import scipy
import scipy.spatial
import time

# TODO: implement serverside caching of distanceMatrix
def getCocktailDistancesFromCacheOrDB():
    MatrixFromDB = CocktailCondensedMatrix.objects.latest("id")
    squaredMatrixFromDB = scipy.spatial.distance.squareform(MatrixFromDB.value)
    np.fill_diagonal(squaredMatrixFromDB, 1.0)

    return pd.DataFrame(data=squaredMatrixFromDB[1:,1:],
                        index=squaredMatrixFromDB[1:,0],
                        columns=squaredMatrixFromDB[0,1:])


def getUserProfile(userID):
    start = time.time()
    cocktailDistanceDataFrame = getCocktailDistancesFromCacheOrDB()
    print(time.time() - start)
    #print(cocktailDistanceDataFrame.loc[[1, 2]])
    #sum_ = cocktailDistanceDataFrame.loc[[1,2]].sum().to_frame().transpose()
    #print(time.time() - start)
    #print(sum_)

    list = []
    for review in Review.objects.filter(user_id=userID):
        #print("new review")
        #print(time.time() - start)
        if review.liked == True:
            curRow = cocktailDistanceDataFrame.loc[[review.cocktail_id]] * 1
        elif review.liked == False:
            curRow = cocktailDistanceDataFrame.loc[[review.cocktail_id]] * -1
        elif review.bookmarked == True:
            curRow = cocktailDistanceDataFrame.loc[[review.cocktail_id]] * 0.5
        elif not review.bookmarked == False:
            curRow = cocktailDistanceDataFrame.loc[[review.cocktail_id]] * -0.5
        list.append(curRow)
        #print("review done at:")
        #print(time.time() - start)

    profile = pd.concat(list)
    print("liste erstellt")
    print(time.time() - start)
    sum_ = profile.sum().to_frame().transpose()
    print(time.time() - start)
    print("berechnung gemacht")
    print(profile)
    print(sum_)
    #print(profile)
    #print(list)
    print(time.time() - start)
