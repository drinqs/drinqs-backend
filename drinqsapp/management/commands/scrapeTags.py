from abc import ABC
import requests
from django.core.management.base import BaseCommand
from drinqsapp.models import Ingredient, IngredientTag
from re import search
import numpy as np
import pandas as pd


def getAllTags(self):

    drinkcategoriesCSV = pd.read_csv("data/drinkCategories.csv")
    drinkcategoriesList = drinkcategoriesCSV["0"]

    foodcategoriesCSV = pd.read_csv("data/foodCategories.csv")
    foodcategoriesList = foodcategoriesCSV["0"]

    for ingredient in Ingredient.objects.all():
        url = 'https://en.wikipedia.org/w/api.php'

        print('Try to search for ingredient...')
        params = dict(
            format='json',
            action='opensearch',
            search=ingredient.name,
            limit=100
        )

        resp = requests.get(url=url, params=params)
        data = resp.json()
        print(data[1])
        if data[1]:
            print('iterate over search result...')
            for searchResult in data[1]:
                print('try... ' + searchResult)
                params = dict(
                    format='json',
                    action='query',
                    prop='categories',
                    cllimit='max',
                    titles=searchResult,
                    redirects='true',
                )

                resp = requests.get(url=url, params=params)
                data = resp.json()
                for page in data["query"]["pages"]:
                    print(ingredient)
                    if page != "-1":
                        if "categories" in data["query"]["pages"][page]:
                            for category in data["query"]["pages"][page]["categories"]:
                                print(category["title"])
                                if category["title"] in drinkcategoriesList.values \
                                    or category["title"] in foodcategoriesList.values:
                                    print("is in list!")
                                    c = category["title"].replace("Category:","")
                                    if len(c) < 127:
                                        ingredient.ingredient_tags.add(IngredientTag.objects.get_or_create(name=c)[0])
                                        print(c + " --- saved into DB")

        else:
            splitString = ingredient.name.split()
            searchSplit = []
            print('Try to search for SPLIT ingredient...' + str(splitString))
            if len(splitString) > 2:
                tempString = splitString.copy()
                del tempString[0]
                withoutFirst = ' '.join(tempString)
                tempString = splitString.copy()
                del tempString[-1]
                withoutLast = ' '.join(tempString)
                searchSplit.append(withoutFirst)
                searchSplit.append(withoutLast)

            for split in searchSplit:
                print('split:' + split)
                params = dict(
                    format='json',
                    action='opensearch',
                    search=split,
                    limit=100
                )

                resp = requests.get(url=url, params=params)
                data = resp.json()
                print(data[1])
                print('iterate over splitted search result...')
                if data[1]:
                    for searchResult in data[1]:
                        print('try... ' + searchResult)
                        params = dict(
                            format='json',
                            action='query',
                            prop='categories',
                            cllimit='max',
                            titles=searchResult,
                            redirects='true',
                        )
                        resp = requests.get(url=url, params=params)
                        data = resp.json()
                        for page in data["query"]["pages"]:
                            print(ingredient)
                            if page != "-1":
                                if "categories" in data["query"]["pages"][page]:
                                    for category in data["query"]["pages"][page]["categories"]:
                                        print(category["title"])
                                        if category["title"] in drinkcategoriesList.values or category[
                                            "title"] in foodcategoriesList.values:
                                            print("is in list!")
                                            c = category["title"].replace("Category:", "")
                                            if len(c) < 127:
                                                ingredient.ingredient_tags.add(
                                                    IngredientTag.objects.get_or_create(name=c)[0])
                                                print(c + " --- saved into DB")

    for ingredient in Ingredient.objects.filter(ingredient_tags__isnull=True):
        url = 'https://en.wikipedia.org/w/api.php'
        splitString = ingredient.name.split()
        print('Try to search for SPLIT ingredient...' + str(splitString))

        for split in splitString:
            print('split:' + split)
            params = dict(
                format='json',
                action='opensearch',
                search=split,
                limit=10
            )

            resp = requests.get(url=url, params=params)
            data = resp.json()
            print(data[1])
            print('iterate over splitted search result...')
            if data[1]:
                for searchResult in data[1]:
                    print('try... ' + searchResult)
                    params = dict(
                        format='json',
                        action='query',
                        prop='categories',
                        cllimit='max',
                        titles=searchResult,
                        redirects='true',
                    )
                    resp = requests.get(url=url, params=params)
                    data = resp.json()
                    for page in data["query"]["pages"]:
                        print(ingredient)
                        if page != "-1":
                            if "categories" in data["query"]["pages"][page]:
                                for category in data["query"]["pages"][page]["categories"]:
                                    print(category["title"])
                                    if category["title"] in drinkcategoriesList.values or category[
                                        "title"] in foodcategoriesList.values:
                                        print("is in list!")
                                        c = category["title"].replace("Category:", "")
                                        if len(c) < 127:
                                            ingredient.ingredient_tags.add(
                                                IngredientTag.objects.get_or_create(name=c)[0])
                                            print(c + " --- saved into DB")


class Command(BaseCommand, ABC):

    def handle(self, *args, **kwargs):
        getAllTags(self)




