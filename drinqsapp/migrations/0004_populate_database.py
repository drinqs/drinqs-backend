from django.db import migrations
from drinqsapp.models import Cocktail, Glass, Ingredient, IngredientTag, CocktailIngredient, Review
import numpy as np
import pandas as pd
import re

def importDatasets(*args):
    return [pd.read_csv(filename) for filename in args]

def cleanDatasets(df1, df2, df3, df4):
    # drop unnecessary columns and rename in a consistent way
    # df1
    df1.drop(columns=['Unnamed: 0', 'dateModified', 'idDrink', 'strVideo', 'strIBA', 'strIngredient13', 'strIngredient14', 'strIngredient15', 'strMeasure13', 'strMeasure14', 'strMeasure15'], errors='ignore', inplace=True)
    df1.rename(columns={'strDrink': 'name', 'strDrinkThumb': 'thumbnailurl', 'strInstructions': 'preparation'}, inplace=True)
    df1.columns = [re.sub(r'^str', '', colname).lower() for colname in df1.columns]

    # df2
    df2.drop(columns=['Bartender', 'Bar/Company', 'Location', 'Garnish', 'Notes'], errors='ignore', inplace=True)
    df2.rename(columns={'Cocktail Name': 'name', 'Glassware':'glass'}, inplace=True)
    df2.rename(str.lower, axis='columns', inplace=True)

    # df3
    df3.drop(columns=['Bartender', 'Bar/Company', 'City', 'Garnish', 'Notes'], errors='ignore', inplace=True)
    df3.rename(columns={'Cocktail Name': 'name', 'Glassware':'glass'}, inplace=True)
    df3.rename(str.lower, axis='columns', inplace=True)

    # df4
    df4.drop(columns=['glass-size'], errors='ignore', inplace=True)
    df4.rename(columns={'instructions' : 'preparation'}, inplace=True)
    df4.columns = [re.sub(r'-', '', colname) for colname in df4.columns]

def joinDatasets(df1, df2, df3, df4):
    # join data sets 2 and 3 as they have the same structure
    return df2.join(df3.set_index(['name', 'glass', 'ingredients', 'preparation']), on=['name', 'glass', 'ingredients', 'preparation'], how='outer')

def populateDatabase(df1, df23, df4):
    # glasses
    glasses = pd.Series(map(lambda x: str(x).title() if isinstance(x, str) else x, df1.glass.append(df23.glass).append(df4.glass))).dropna().drop_duplicates().sort_values(ignore_index=True)
    f'all datasets contain {len(glasses)} unique glasses in total'
    for glass in glasses: Glass.objects.create(name=glass).save()

    # ingredients for df1 and df4
    ingredients = pd.Series(dtype='str')
    for i in range(1, sum('ingredient' in col for col in df1.columns) + 1):
        # if i%2 == 0: ingredients = ingredients.append(df4[f'ingredient{int(i/2)}'].dropna())
        ingredients = ingredients.append(df1[f'ingredient{i}'].dropna())
    ingredients = pd.Series(map(str.title, ingredients)) # change ingredient name to title case
    ingredients = pd.Series(map(str.strip, ingredients)).dropna().drop_duplicates().sort_values(ignore_index=True) # remove whitespaces
    f'datasets 1 and 4 contain {len(ingredients)} unique ingredients'
    for ingredient in ingredients: Ingredient.objects.create(name=ingredient).save()

    # cocktails and recipes in df1
    for cocktail in df1.iloc:
        try: glass = Glass.objects.get(name=str(cocktail.glass).title())
        except Glass.DoesNotExist: glass = None
        alc = 2 if 'No' in str(cocktail.alcoholic) or 'Optional' in str(cocktail.alcoholic) else 1 if str(cocktail.alcoholic) == 'Alcoholic' else 0
        cocktailObject = Cocktail.objects.create(name=cocktail['name'], alcoholic=alc, category=cocktail.category, preparation=cocktail.preparation, thumbnail_url=cocktail.thumbnailurl, glass=glass)
        cocktailObject.save()
        for i in range(1, sum('ingredient' in col for col in df1.columns) + 1):
            if isinstance(cocktail[f'ingredient{i}'], str):
                ingredientObject = Ingredient.objects.get(name=cocktail[f'ingredient{i}'].strip().title())
                measurement = cocktail[f'measure{i}'].strip() if isinstance(cocktail[f'measure{i}'], str) else None
                CocktailIngredient.objects.create(measurement=measurement, position=1, cocktail=cocktailObject, ingredient=ingredientObject).save()

    # # cocktails and recipes in df4
    # for cocktail in df4.iloc:
    #     try: Cocktail.objects.get(name=cocktail['name'])
    #     except Cocktail.DoesNotExist:
    #         try: glass = Glass.objects.get(name=str(cocktail.glass).title())
    #         except Glass.DoesNotExist: glass = None
    #         cocktailObject = Cocktail.objects.create(name=cocktail['name'], alcoholic=0, category=cocktail.category, preparation=cocktail.preparation, thumbnail_url='', glass=glass)
    #         cocktailObject.save()
    #         for i in range(1, sum('ingredient' in col for col in df4.columns) + 1):
    #             if isinstance(cocktail[f'ingredient{i}'], str):
    #                 ingredientObject = Ingredient.objects.get(name=cocktail[f'ingredient{i}'].strip().title())
    #                 measurement = cocktail[f'measurement{i}'].strip() if isinstance(cocktail[f'measurement{i}'], str) else None
    #                 CocktailIngredient.objects.create(measurement=measurement, position=1, cocktail=cocktailObject, ingredient=ingredientObject).save()



def populate(apps, schema_editor):
    df1, df2, df3, df4 = importDatasets('data/all_drinks.csv', 'data/hotaling_cocktails.csv', 'data/hotaling_cocktails2.csv', 'data/mr-boston-flattened.csv')
    cleanDatasets(df1 = df1, df2 = df2, df3 = df3, df4 = df4)
    df23 = joinDatasets(df1 = df1, df2 = df2, df3 = df3, df4 = df4)
    populateDatabase(df1 = df1, df23 = df23, df4 = df4)

class Migration(migrations.Migration):

    dependencies = [
        ('drinqsapp', '0003_auto_20210124_1945'),
    ]

    operations = [
        migrations.RunPython(populate),
    ]
