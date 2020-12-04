from django.db import models
from django.contrib.auth import models as authmodels

# Models for drinqs application.
# (E) Entity model
# (R) Relationship model: A-B
# User model (E) inherited from django.contrib.auth.models


# (E) Cocktail
class Cocktail(models.Model):
    # Alcoholic Enumeration
    class Alcoholic(models.IntegerChoices):
        NA = 0, 'not available'
        YES = 1, 'alcoholic'
        NO = 2, 'non alcoholic'
    name = models.CharField(max_length=128)
    alcoholic = models.IntegerField(choices=Alcoholic.choices)
    category = models.CharField(max_length=128)
    preparation = models.CharField(max_length=1024)
    thumbnailUrl = models.CharField(max_length=512)
    ingredients = models.ManyToManyField('Ingredient', through='CocktailHasIngredient')
    review = models.ManyToManyField(authmodels.User, through='Reviewed')
    characteristic = models.ManyToManyField('Characteristic')
    glass = models.ManyToManyField('Glass')
    def __str__(self):
        return self.name

# (E) Glass
class Glass(models.Model):
    name = models.CharField(max_length=128)
    def __str__(self):
        return self.name

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
    amount = models.IntegerField()
    position = models.SmallIntegerField()
    cocktail = models.ForeignKey('Cocktail', on_delete=models.CASCADE)
    ingredient = models.ForeignKey('Ingredient', on_delete=models.CASCADE)
    def __str__(self):
        return self.measurement

# (E) Ingredient
class Ingredient(models.Model):
    name = models.CharField(max_length=128)
    ingredientType = models.ForeignKey('IngredientType', blank=False, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

# (E) Ingredient Type
class IngredientType(models.Model):
    name = models.CharField(max_length=128)
    user = models.ManyToManyField(authmodels.User, blank=True)
    def __str__(self):
        return self.name

# (R) Reviewed: User-Cocktail
class Reviewed(models.Model):
    # Likes Enumeration
    class Likes(models.IntegerChoices):
        NA = 0, 'not available'
        YES = 1, 'likes'
        NO = 2, 'dislikes'
    user = models.ForeignKey(authmodels.User, blank=True, on_delete=models.CASCADE)
    cocktail = models.ForeignKey('Cocktail', blank=True, on_delete=models.CASCADE)
    likes = models.IntegerField(choices=Likes.choices)
    def __str__(self):
        return str(self.user)

# (E) Characteristic
class Characteristic(models.Model):
    name = models.CharField(max_length=128)
    user = models.ManyToManyField(authmodels.User, blank=True)
    def __str__(self):
        return self.name