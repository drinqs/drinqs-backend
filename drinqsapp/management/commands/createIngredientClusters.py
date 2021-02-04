from abc import ABC
import requests
from django.core.management.base import BaseCommand
from drinqsapp.models import Ingredient, IngredientTag
from re import search
import numpy as np
import pandas as pd


# creates a matrix between all ingredients and all ingredient_tags
# first row = ingredientID
# first col = ingredientTag_ID
def createIngredient_IngredientTag_Matrix():
    matrix = np.zeros((Ingredient.objects.all().count()+1, IngredientTag.objects.all().count()+1), dtype=int, order='C')

    counter = 1
    for ingredient_tag in IngredientTag.objects.order_by("id").all():
        matrix[0, counter] = ingredient_tag.id
        counter=counter+1

    counter = 1
    for ingredient in Ingredient.objects.order_by("id").all():
        matrix[counter, 0] = ingredient.id
        counter = counter + 1


    OnlyFirstCol = matrix[0:,0:1]
    OnlyFirstRow = matrix[0]

    #print(matrix[0])
    for ingredient in Ingredient.objects.all():
        row_id = np.argwhere(OnlyFirstCol == ingredient.id)[0][0]
        #print('ingredient_id: ' + str(ingredient.id))
        #print('row_id: ' + str(row_id))
        for ingredient_tag in ingredient.ingredient_tags.all():
            col_id= np.where(OnlyFirstRow == ingredient_tag.id)[0][0]
            #print('tag_id: '+ str(ingredient_tag.id))
            #print('located:' + str(col_id))
            matrix[row_id, col_id] = 1

    return matrix

class Command(BaseCommand, ABC):

    def handle(self, *args, **kwargs):
        test = createIngredient_IngredientTag_Matrix()

        print(test[5])
        print(test[6])



