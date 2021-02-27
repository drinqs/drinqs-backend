import requests
import json
import scrape_cocktaildb, filing


def alphabet_api():
    alphabet = 'abcdefghijklmnopqrstvwyz12345679'
    json_nach_alphabet = {}
    for letter in alphabet:
        response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/search.php?f=%s' % letter)
        jsondrinks = response.json()['drinks']
        json_nach_alphabet[letter] = jsondrinks
    return json_nach_alphabet


def get_names():
    jsonList = alphabet_api()
    nameList = []
    for letter in jsonList:
        for part in jsonList[letter]:
            name = part['strDrink']
            nameList.append(name)
    return nameList


def get_json():
    jsondict = alphabet_api()
    jsonlist = []
    for letter in jsondict:
        for part in jsondict[letter]:
            jsonlist.append(part)
    return jsonlist


def api_to_file():
    alphabet = 'abcdefghijklmnopqrstvwyz12345679'
    jsondict = alphabet_api()
    liste = []
    for letter in alphabet:
        for drink in jsondict[letter]:
            liste.append(drink)
    dict = {'drinks': liste}
    with open('cocktails.json', 'r+')as file:
        json.dump(dict, file)


def detect_missing_cocktails():
    apinames = get_names()
    print('got API names')
    scrapenames = scrape_cocktaildb.scrapeNames()
    print('got scrape names')
    fehlende = set(scrapenames).difference(set(apinames))
    return fehlende


def get_missing_cocktails():
    """ Creates a list (all missing cocktails) with dictionaries containing the information"""
    names = sorted(list(detect_missing_cocktails()))
    print('Got missing cocktails')
    json_list = []
    print('start requests for missing Cocktails')
    for drink in names:
        # print('request:', drink)
        response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/search.php?s=%s' % drink)
        # print(response.status_code)
        jsondrinks = response.json()['drinks'][0]
        json_list.append(jsondrinks)
    print('all requests made')
    return json_list


def get_ingredient_tag():
    ingredients = filing.ingredient_list()
    ingre_dict = {}
    for ingredient in ingredients:
        response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/search.php?i=%s'%ingredient)
        print(ingredient)
        if response.json()['ingredients'] is None:
            ingre_dict[ingredient] = ['', '']
        else:
            jsoningred = response.json()['ingredients'][0]
            ingre_dict[jsoningred["strIngredient"]] = []
            ingre_dict[jsoningred["strIngredient"]].append(jsoningred["strType"])
            ingre_dict[jsoningred["strIngredient"]].append(jsoningred["strAlcohol"])
            if ingre_dict[jsoningred["strIngredient"]][0] is None:
                ingre_dict[jsoningred["strIngredient"]][0] = ''
            if ingre_dict[jsoningred["strIngredient"]][1] is None:
                ingre_dict[jsoningred["strIngredient"]][1] = 'No'
    return ingre_dict
