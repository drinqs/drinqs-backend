import json


def ingredient_list():
    with open('cocktails.json') as fi:
        drinklist = json.load(fi)
        ingredients = []
        ingredientnum = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
        for ele in drinklist:
            for number in ingredientnum:
                ingredients.append(str(ele['strIngredient%i' % number]).lower())
        newlist = set(ingredients)
        ingredients = list(newlist)
        ingredients.remove('none')
        ingredients.remove('')
        ingredients.sort()
    return ingredients
