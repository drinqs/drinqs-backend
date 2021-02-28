from abc import ABC
import pandas as pd
import requests
from django.core.management.base import BaseCommand
from drinqsapp.models import Ingredient, IngredientTag


def get_all_tags(self):

    drinkcategories_csv = pd.read_csv("data/drinkCategories.csv")
    drinkcategories_list = drinkcategories_csv["0"]

    foodcategories_csv = pd.read_csv("data/foodCategories.csv")
    foodcategories_list = foodcategories_csv["0"]

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
            for search_result in data[1]:
                print('try... ' + search_result)
                params = dict(
                    format='json',
                    action='query',
                    prop='categories',
                    cllimit='max',
                    titles=search_result,
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
                                if category["title"] in drinkcategories_list.values \
                                    or category["title"] in foodcategories_list.values:
                                    print("is in list!")
                                    cat = category["title"].replace("Category:","")
                                    if len(cat) < 127:
                                        ingredient.ingredient_tags.add(IngredientTag.objects.get_or_create(name=cat)[0])
                                        print(cat + " --- saved into DB")

        else:
            split_string = ingredient.name.split()
            search_split = []
            print('Try to search for SPLIT ingredient...' + str(split_string))
            if len(split_string) > 2:
                temp_string = split_string.copy()
                del temp_string[0]
                without_first = ' '.join(temp_string)
                temp_string = split_string.copy()
                del temp_string[-1]
                without_last = ' '.join(temp_string)
                search_split.append(without_first)
                search_split.append(without_last)

            for split in search_split:
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
                    for search_result in data[1]:
                        print('try... ' + search_result)
                        params = dict(
                            format='json',
                            action='query',
                            prop='categories',
                            cllimit='max',
                            titles=search_result,
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
                                        if category["title"] in drinkcategories_list.values or category[
                                                "title"] in foodcategories_list.values:
                                            print("is in list!")
                                            cat = category["title"].replace("Category:", "")
                                            if len(cat) < 127:
                                                ingredient.ingredient_tags.add(
                                                    IngredientTag.objects.get_or_create(name=cat)[0])
                                                print(cat + " --- saved into DB")

    for ingredient in Ingredient.objects.filter(ingredient_tags__isnull=True):
        url = 'https://en.wikipedia.org/w/api.php'
        split_string = ingredient.name.split()
        print('Try to search for SPLIT ingredient...' + str(split_string))

        for split in split_string:
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
                for search_result in data[1]:
                    print('try... ' + search_result)
                    params = dict(
                        format='json',
                        action='query',
                        prop='categories',
                        cllimit='max',
                        titles=search_result,
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
                                    if category["title"] in drinkcategories_list.values or category[
                                            "title"] in foodcategories_list.values:
                                        print("is in list!")
                                        cat = category["title"].replace("Category:", "")
                                        if len(cat) < 127:
                                            ingredient.ingredient_tags.add(
                                                IngredientTag.objects.get_or_create(name=cat)[0])
                                            print(cat + " --- saved into DB")


class Command(BaseCommand, ABC):
    def handle(self, *args, **kwargs):
        get_all_tags(self)
