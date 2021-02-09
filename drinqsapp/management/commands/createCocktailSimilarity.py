from abc import ABC
import requests
from django.core.management.base import BaseCommand
from drinqsapp.models import Ingredient, IngredientTag, Cocktail, CocktailCondensedMatrix
from itertools import islice
from re import search
import numpy as np
import pandas as pd
import sklearn.cluster as cluster
from sklearn.cluster import AgglomerativeClustering
import time
import math
from sklearn.datasets import load_iris
from scipy.cluster import hierarchy
import scipy
import scipy.spatial


# creates a matrix between all ingredients and all ingredient_tags
# first row = ingredientID
# first col = ingredientTag_ID
def create_ingredient_ingredienttag_matrix():
    matrix = np.zeros((Ingredient.objects.all().count() + 1, IngredientTag.objects.all().count() + 1),
                      dtype=int, order='C')

    counter = 1
    for ingredient_tag in IngredientTag.objects.order_by("id").all():
        matrix[0, counter] = ingredient_tag.id
        counter = counter + 1
    counter = 1
    for ingredient in Ingredient.objects.order_by("id").all():
        matrix[counter, 0] = ingredient.id
        counter = counter + 1

    OnlyFirstCol = matrix[0:, 0:1]
    OnlyFirstRow = matrix[0]

    # print(matrix[0])
    for ingredient in Ingredient.objects.all():
        row_id = np.argwhere(OnlyFirstCol == ingredient.id)[0][0]
        # print('ingredient_id: ' + str(ingredient.id))
        # print('row_id: ' + str(row_id))
        for ingredient_tag in ingredient.ingredient_tags.all():
            col_id = np.where(OnlyFirstRow == ingredient_tag.id)[0][0]
            # print('tag_id: '+ str(ingredient_tag.id))
            # print('located:' + str(col_id))
            matrix[row_id, col_id] = 1

    return matrix


# Similarity
def magnitude(vector):
    return math.sqrt(np.dot(vector, vector))


def cosine_similarity(a, b):
    result = magnitude(a) * magnitude(b)
    if result == 0:
        return 0
    else:
        return np.dot(a, b) / result


# creates a similarity matrix between all ingredients and all ingredient_tags based on cosine similarity
# first row = ingredientID
# first col = ingredientTag_ID
def create_similarity_matrix(matrix):
    just_values = matrix[1:, 1:]
    distance = np.zeros((len(just_values), len(just_values)), dtype=float, order='C')

    for i in range(0, len(just_values)):
        for j in range(0, len(just_values)):
            distance[i][j] = cosine_similarity(just_values[i], just_values[j])

    return distance


def create_condensed_distance_matrix(matrix, metric):
    just_values = matrix[1:,1:]
    condensed_matrix = scipy.spatial.distance.pdist(just_values, metric=metric)
    for i in range(0, len(condensed_matrix)):
        if not np.isfinite(condensed_matrix[i]):
            condensed_matrix[i] = 0.0
    return condensed_matrix


def create_ingredient_clusters(condensedMatrix, method, threshold, metric, criterion, withIDs):
    clusterMethod = hierarchy.linkage(condensedMatrix,method=method, metric=metric)
    cluster_result = hierarchy.fcluster(clusterMethod, threshold, criterion=criterion)

    if withIDs:
        cluster_with_ids = np.c_[np.zeros(len(cluster_result)), cluster_result]
        counter = 0
        for ingredient in Ingredient.objects.order_by("id").all():
            cluster_with_ids[counter, 0] = ingredient.id
            counter = counter + 1
        return cluster_with_ids
    else:
        return cluster_result

def create_cocktail_ingredientCluster_matrix(clustered_Ingredients):

    SecondCol = clustered_Ingredients[0:, 1:2]
    matrix = np.zeros((Cocktail.objects.all().count() + 1, np.amax(SecondCol).astype(int) + 1),
                      dtype=int, order='C')

    counter = 1
    for cocktail in Cocktail.objects.order_by("id").all():
        matrix[counter, 0] = cocktail.id
        counter = counter + 1
    for i in range(1, len(matrix[0])):
        matrix[0, i] = i

    OnlyFirstColMatrix = matrix[0:, 0:1]
    OnlyFirstRowMatrix = matrix[0]

    OnlyFirstColInput =  clustered_Ingredients[0:, 0:1]

    for cocktail in Cocktail.objects.all():
        row_id = np.argwhere(OnlyFirstColMatrix == cocktail.id)[0][0]

        for ingredient in cocktail.ingredients.all():
            cluster_col_id = np.where(OnlyFirstColInput == ingredient.id)[0][0]
            cluster_id = clustered_Ingredients[cluster_col_id, 1]
            col_id =  np.where(OnlyFirstRowMatrix == cluster_id)[0][0]

            matrix[row_id, col_id] = matrix[row_id, col_id] + 1

    return matrix

class Command(BaseCommand, ABC):
    def handle(self, *args, **kwargs):

        ##clustering
        ingredient_tag_matrix = create_ingredient_ingredienttag_matrix()
        condensed_matrix = create_condensed_distance_matrix(ingredient_tag_matrix, 'cosine')
        squared_matrix = scipy.spatial.distance.squareform(condensed_matrix)
        clustered_ingredients = create_ingredient_clusters(condensedMatrix=condensed_matrix, method='ward',
                                             threshold=1.2, metric='cosine', criterion='distance',
                                             withIDs=True)

        ##cocktail similarity
        cocktail_ingrCluster_matrix = create_cocktail_ingredientCluster_matrix(clustered_ingredients)

        condensed_simil_matrix = create_condensed_distance_matrix(cocktail_ingrCluster_matrix, metric=cosine_similarity)
        squared_simil_matrix = scipy.spatial.distance.squareform(condensed_simil_matrix)
        squared_simil_matrix_WithIds = np.r_[np.transpose(cocktail_ingrCluster_matrix[1:, 0:1]), squared_simil_matrix]
        squared_simil_matrix_WithIds = np.c_[cocktail_ingrCluster_matrix[0:, 0:1], squared_simil_matrix_WithIds]
        condensed_simil_matrix_WithIds = scipy.spatial.distance.squareform(squared_simil_matrix_WithIds)


        simil_list = list(condensed_simil_matrix_WithIds)
        cocktailCondensedMatrix = CocktailCondensedMatrix(value=simil_list)
        cocktailCondensedMatrix.save()
