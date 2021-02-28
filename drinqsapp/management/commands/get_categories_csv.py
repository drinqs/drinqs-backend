from abc import ABC
from re import search
import requests
import numpy as np
import pandas as pd
from django.core.management.base import BaseCommand


def create_wiki_category_tree(category, result, regex_filter):
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
        if not search(regex_filter, category['title']) and category['title'] not in result:
            print(category['title'])
            result.append(category['title'])
            result = create_wiki_category_tree(category=category['title'], result=result, regex_filter=regex_filter)

    return result


class Command(BaseCommand, ABC):

    def handle(self, *args, **kwargs):
        drinks_regex_filter = "[C|c]ompanies|[B|b]rewer[i|y]|[P|p]ubs|continent|country|region|brewers|" \
                              "industry|culture|organizations|[P|p]eople|logos|[W|w]ineries|industr|establishment|" \
                              "[H|h]ot springs|[G|g]eographical|science|[H|h]istory|Cocktails"

        food_regex_filter = "[C|c]ompanies|[B|b]rewer[i|y]|[P|p]ubs|continent|country|region|brewers|" \
                            "industry|culture|organizations|[P|p]eople|logos|[W|w]ineries|industr|establishment|" \
                            "[H|h]ot springs|[G|g]eographical|science|[H|h]istory|product brands|prepared|technique|by type|Lists|" \
                            "Condiments|Cuisine|Dips|excrement|combinations|logos|Meat|Pizza|Wedding food|Water|" \
                            "McDonald|plantation|Oils|pastries|[C|c]ake|Cocktails"
        foodcategories = create_wiki_category_tree(category='Category:Foods', result=[]
                                                   , regex_filter=food_regex_filter)
        foods = np.asarray(foodcategories)
        pd.DataFrame(foods).to_csv("data/foodCategories.csv")

        drinkcategories = create_wiki_category_tree(category='Category:Drinks', result=[]
                                                    , regex_filter=drinks_regex_filter)
        drinks = np.asarray(drinkcategories)
        pd.DataFrame(drinks).to_csv("data/drinkCategories.csv")
