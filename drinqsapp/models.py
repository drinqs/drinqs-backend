from django.db import models
from django.db.models import UniqueConstraint
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
    name = models.CharField(max_length=128, unique=True)
    alcoholic = models.IntegerField(choices=Alcoholic.choices)
    category = models.CharField(max_length=128)
    preparation = models.CharField(max_length=2048)
    thumbnailurl = models.CharField(max_length=512)
    ingredients = models.ManyToManyField('Ingredient', through='CocktailIngredients')
    userReview = models.ManyToManyField(authmodels.User, through='Review')
    glass = models.ForeignKey('Glass', blank=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

# (E) Glass
class Glass(models.Model):
    name = models.CharField(max_length=128, unique=True)
    def __str__(self):
        return self.name

# (R) CocktailIngredients: Cocktail-Ingredient
class CocktailIngredients(models.Model):
    class Meta:
        constraints = [
            # Ensure there is only one entry per cocktail-ingredient combination
            UniqueConstraint(fields=['cocktail', 'ingredient'], name='unique_cocktailingredients')
        ]
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
        return str(self.cocktail)

# (E) Ingredient
class Ingredient(models.Model):
    name = models.CharField(max_length=128, unique=True)
    ingredienttag = models.ManyToManyField('IngredientTag', blank=True)
    def __str__(self):
        return self.name

# (E) Ingredient Tag
class IngredientTag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    user = models.ManyToManyField(authmodels.User, blank=True)
    def __str__(self):
        return self.name

# (R) Review: User-Cocktail
class Review(models.Model):
    class Meta:
        constraints = [
            # Ensure that a review is only created once and then updated if necessary
            UniqueConstraint(fields=['user', 'cocktail'], name='unique_review')
        ]
    user = models.ForeignKey(authmodels.User, on_delete=models.CASCADE)
    cocktail = models.ForeignKey('Cocktail', on_delete=models.CASCADE)
    likes = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)