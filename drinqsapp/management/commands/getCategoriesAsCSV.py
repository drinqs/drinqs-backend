from abc import ABC
import requests
from django.core.management.base import BaseCommand
from drinqsapp.models import Ingredient, IngredientTag
from re import search
import numpy as np
import pandas as pd


def createWikiCategoryTree(category, result, regexFilter):
    url = 'https://en.wikipedia.org/w/api.php'

    params = dict(
        format='json',
        action='query',
        list='categorymembers',
        cmtitle=category,
        cmlimit='max',
        cmtype='subcat'
    )

    resp = requests.get(url=url, params=params)
    data = resp.json()

    for category in data["query"]["categorymembers"]:
        if not search(regexFilter, category['title']) and category['title'] not in result:
            print(category['title'])
            result.append(category['title'])
            result = createWikiCategoryTree(category=category['title'], result=result, regexFilter=regexFilter)

    return result

class Command(BaseCommand, ABC):

    def handle(self, *args, **kwargs):

        drinksRegexFilter = "[C|c]ompanies|[B|b]rewer[i|y]|[P|p]ubs|continent|country|region|brewers|" \
                    "industry|culture|organizations|[P|p]eople|logos|[W|w]ineries|industr|establishment|" \
                    "[H|h]ot springs|[G|g]eographical|science|[H|h]istory|Cocktails"

        foodRegexFilter = "[C|c]ompanies|[B|b]rewer[i|y]|[P|p]ubs|continent|country|region|brewers|" \
                        "industry|culture|organizations|[P|p]eople|logos|[W|w]ineries|industr|establishment|" \
                        "[H|h]ot springs|[G|g]eographical|science|[H|h]istory|product brands|prepared|technique|by type|Lists|" \
                        "Condiments|Cuisine|Dips|excrement|combinations|logos|Meat|Pizza|Wedding food|Water|" \
                        "McDonald|plantation|Oils|pastries|[C|c]ake|Cocktails"

        foodcategories = createWikiCategoryTree(category='Category:Foods', result=[]
                                            ,regexFilter=foodRegexFilter)
        foods = np.asarray(foodcategories)
        pd.DataFrame(foods).to_csv("data/foodCategories.csv")

        drinkcategories = createWikiCategoryTree(category='Category:Drinks', result=[]
                                            ,regexFilter=drinksRegexFilter)
        drinks = np.asarray(drinkcategories)
        pd.DataFrame(drinks).to_csv("data/drinkCategories.csv")


