from abc import ABC
from django.core.management.base import BaseCommand
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from drinqsapp.models import Ingredient, IngredientTag, Cocktail, CocktailCondensedMatrix
import math
import numpy as np
import scipy
from scipy.cluster import hierarchy
import scipy.spatial

class Command(BaseCommand, ABC):
    def handle(self, *args, **kwargs):
        # Clustering of Ingredients
        ingredient_tag_matrix = self.__compute_ingredient_tag_matrix()
        ingredient_distance_matrix = self.__compute_condensed_distance_matrix(ingredient_tag_matrix, metric='cosine')
        clustered_ingredients = self.__create_ingredient_clusters(
            matrix=ingredient_distance_matrix,
            method='ward',
            threshold=1.2,
            metric='cosine',
            criterion='distance',
            with_ids=True,
        )

        # Compute Cocktail Similarity
        cocktail_similarity_matrix = self.__compute_cocktail_similarity_matrix(clustered_ingredients)
        condensed_cocktail_similarity_matrix = scipy.spatial.distance.squareform(cocktail_similarity_matrix)

        # Save Cocktail Similarity Matrix to DB
        cocktail_condensed_matrix = CocktailCondensedMatrix(value=list(condensed_cocktail_similarity_matrix))
        cocktail_condensed_matrix.save()


    def __compute_ingredient_tag_matrix(self):
        '''
        Creates a matrix between all Ingredients and all IngredientTags.\n
        Columns are the IngredientTag IDs, while rows are Ingredient IDs.\n
        A cell indicates how many ingredients of a cocktail belong to an ingredient cluster.\n
        \n
        |   | 1 | 2 | 3 | … |
        |:-:|:-:|:-:|:-:|:-:|
        | 1 | 0 | 0 | 1 | … |
        | … | … | … | … | … |
        '''

        ingredient_tag_ids = list(IngredientTag.objects.order_by("id").values_list("id", flat=True))
        ingredient_ids = list(Ingredient.objects.order_by("id").values_list("id", flat=True))
        matrix = np.zeros((len(ingredient_ids) + 1, len(ingredient_tag_ids) + 1), dtype=int, order='C')

        matrix[0, 1:] = ingredient_tag_ids
        matrix[1:, 0] = ingredient_ids

        ingredients_with_tag_ids = list(
            Ingredient.objects
                .annotate(
                    ingredient_tag_ids=ArrayAgg(
                        'ingredient_tags__id',
                        filter=~Q(ingredient_tags__id=None)
                    )
                )
                .order_by('id')
                .values_list('id', 'ingredient_tag_ids')
        )

        ingredient_ids_in_matrix = matrix[:, 0]
        ingredient_tag_ids_in_matrix = matrix[0, :]

        for ingredient_id, ingredient_tag_ids in ingredients_with_tag_ids:
            ingredient_index = np.where(ingredient_ids_in_matrix == ingredient_id)[0][0]
            for ingredient_tag_id in ingredient_tag_ids:
                ingredient_tag_index = np.where(ingredient_tag_ids_in_matrix == ingredient_tag_id)[0][0]
                matrix[ingredient_index, ingredient_tag_index] = 1

        return matrix

    def __compute_condensed_distance_matrix(self, matrix, metric):
        '''
        Creates a similarity matrix between all Ingredients based on cosine similarity
        regarding their IngredientTags.
        \n
        | 0.22 | 0.44 | 0.8 | … |
        |:----:|:----:|:---:|:-:|
        | …    | …    | …   | … |
        \n
        And returns thie 1-dimesnional condensed matrix.
        '''

        just_values = matrix[1:,1:]
        condensed_matrix = scipy.spatial.distance.pdist(just_values, metric=metric)
        for i in range(0, len(condensed_matrix)):
            if not np.isfinite(condensed_matrix[i]):
                condensed_matrix[i] = 0.0
        return condensed_matrix


    def __create_ingredient_clusters(self, matrix, method, threshold, metric, criterion, with_ids=False):
        cluster_method = hierarchy.linkage(matrix, method=method, metric=metric)
        cluster_result = hierarchy.fcluster(cluster_method, threshold, criterion=criterion)

        if with_ids:
            cluster_with_ids = np.c_[np.zeros(len(cluster_result), dtype=int), cluster_result]
            ingredient_ids = Ingredient.objects.order_by("id").values_list("id", flat=True)
            for index, ingredient_id in enumerate(ingredient_ids):
                cluster_with_ids[index, 0] = ingredient_id
            return cluster_with_ids
        else:
            return cluster_result

    def __create_cocktail_ingredient_cluster_matrix(self, clustered_ingredients):
        '''
        Creates a matrix between all Cocktails and all given Ingredient Clusters.\n
        Columns are the Cluster IDs, while rows are Cocktail IDs.\n
        A cell indicates how many ingredients of a cocktail belong to an ingredient cluster.\n
        \n
        |   | 1 | 2 | 3 | … |
        |:-:|:-:|:-:|:-:|:-:|
        | 1 | 0 | 2 | 1 | … |
        | … | … | … | … | … |
        '''

        cluster_ids = clustered_ingredients[:, 1:].flatten()
        cocktail_ids = list(Cocktail.objects.order_by("id").values_list("id", flat=True))
        matrix = np.zeros((len(cocktail_ids) + 1, cluster_ids.max() + 1), dtype=int, order='C')

        # Set first row to consist of all Cluster IDs
        matrix[0, 1:] = list(range(1, cluster_ids.max() + 1))
        # Set first column to consist of all Cocktail IDs
        matrix[1:, 0] = cocktail_ids

        cocktails_with_ingredient_ids = list(
            Cocktail.objects
                .annotate(
                    ingredient_ids=ArrayAgg(
                        'ingredients__id',
                        filter=~Q(ingredients__id=None)
                    )
                )
                .order_by('id')
                .values_list('id', 'ingredient_ids')
        )

        cocktail_ids_in_matrix = matrix[:, 0]
        ingredient_ids_in_clusters = clustered_ingredients[:, 0]

        for cocktail_id, ingredient_ids in cocktails_with_ingredient_ids:
            cocktail_index = np.where(cocktail_ids_in_matrix == cocktail_id)[0][0]
            for ingredient_id in ingredient_ids:
                cluster_row_index = np.where(ingredient_ids_in_clusters == ingredient_id)[0][0]
                cluster_id = clustered_ingredients[cluster_row_index, 1]
                matrix[cocktail_index, cluster_id] = matrix[cocktail_id, cluster_id] + 1

        return matrix

    def __compute_cocktail_similarity_matrix(self, clustered_ingredients):
        '''
        Generates a Cocktail Similarity Matrix of the form:\n
        \n
        |   | 1   | 2    | 3 | … |
        |:-:|:---:|:----:|:-:|:-:|
        | 1 | 0.4 | 0.75 | 0 | … |
        | … | …   | …    | … | … |
        \n
        where the first column and the first row consist of the existing cocktail IDs.\n
        This enables the result of the Matrix being used in the manner:

        `matrix[cocktail_id, other_cocktail_id]`\n
        `#=> 0.75 (similarity between both cocktails)`
        '''

        # Similarity Helpers
        def magnitude(vector):
            return math.sqrt(np.dot(vector, vector))

        def cosine_similarity(a, b):
            result = magnitude(a) * magnitude(b)
            if result == 0:
                return 0
            else:
                return np.dot(a, b) / result

        cocktail_ingredient_cluster_matrix = self.__create_cocktail_ingredient_cluster_matrix(clustered_ingredients)

        condensed_cocktail_similarity_matrix = self.__compute_condensed_distance_matrix(cocktail_ingredient_cluster_matrix, metric=cosine_similarity)
        cocktail_similarity_matrix = scipy.spatial.distance.squareform(condensed_cocktail_similarity_matrix)

        cocktail_similarity_matrix_with_ids = np.r_[np.transpose(cocktail_ingredient_cluster_matrix[1:, :1]), cocktail_similarity_matrix]
        cocktail_similarity_matrix_with_ids = np.c_[cocktail_ingredient_cluster_matrix[:, :1], cocktail_similarity_matrix_with_ids]

        return cocktail_similarity_matrix_with_ids
