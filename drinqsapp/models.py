from django.db import models
from django.contrib.auth import models as authmodels

# Models for drinqs application.
# (E) Entity model
# (R) Relationship model: A-B
# User model (E) inherited from django.contrib.auth.models


# (E) Cocktail
class Cocktail(models.Model):
    name = models.CharField(max_length=128)
    alcoholic = models.BooleanField
    category = models.CharField(max_length=128)
    preparation = models.CharField(max_length=1024)
    thumbnailUrl = models.CharField(max_length=512)
    ingredients = models.ManyToManyField('Ingredient', through='CocktailHasIngredient')
    review = models.ManyToManyField(authmodels.User, through='Reviewed')
    characteristic = models.ManyToManyField('Characteristic')
    glass = models.ManyToManyField('Glass')

# (E) Glass
class Glass(models.Model):
    name = models.CharField(max_length=128)

# (R) CocktailHasIngredient: Cocktail-Ingredient
class CocktailHasIngredient(models.Model):
    # Measurement Enumeration
    class Measurement(models.IntegerChoices):
        ML = 0, 'ml'
        OZ = 1, 'oz'
        CUP = 2, 'cup'
        TSP = 3, 'tsp'
        TBSP = 4, 'Tbsp'
        PACKAGE = 5, 'package'
    measurement = models.IntegerField(choices=Measurement.choices)
    amount = models.IntegerField
    position = models.SmallIntegerField
    cocktail = models.ForeignKey('Cocktail', on_delete=models.CASCADE)
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE)

# (E) Ingredient
class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    ingredientType = models.ForeignKey('IngredientType', blank=False, on_delete=models.CASCADE)

# (E) Ingredient Type
class IngredientType(models.Model):
    name = models.CharField(max_length=128)
    user = models.ManyToManyField(authmodels.User, blank=True)

# (R) Reviewed: User-Cocktail
class Reviewed(models.Model):
    user = models.ForeignKey(authmodels.User, blank=True, on_delete=models.CASCADE)
    cocktail = models.ForeignKey('Cocktail', blank=True, on_delete=models.CASCADE)
    likes = models.BooleanField

# (E) Characteristic
class Characteristic(models.Model):
    name = models.CharField(max_length=128)
    user = models.ManyToManyField(authmodels.User, blank=True)