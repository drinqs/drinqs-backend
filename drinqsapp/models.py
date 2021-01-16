from django.db import models
from django.db.models import UniqueConstraint
from django.contrib.auth import models as authmodels

# Models for drinqs application.
# (E) Entity model
# (R) Relationship model: A-B
# User model (E) inherited from django.contrib.auth.models

# (E) Glass
class Glass(models.Model):
    name = models.CharField(max_length=128, unique=True)
    def __str__(self):
        return self.name

# (E) Ingredient Tag
class IngredientTag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    user = models.ManyToManyField(authmodels.User, blank=True)
    def __str__(self):
        return self.name

# (E) Ingredient
class Ingredient(models.Model):
    name = models.CharField(max_length=128, unique=True)
    ingredienttag = models.ManyToManyField(IngredientTag, blank=True)
    def __str__(self):
        return self.name

# (E) Cocktail
class Cocktail(models.Model):
    name = models.CharField(max_length=128, unique=True)
    alcoholic = models.IntegerField(blank=True, null=True,
    choices =(
        (0, 'not available'),
        (1, 'alcoholic'),
        (2, 'non alcoholic')
        ),
    )
    category = models.CharField(max_length=128, blank=True, null=True)
    preparation = models.TextField(blank=True, null=True)
    thumbnailurl = models.CharField(max_length=512, blank=True, null=True)
    ingredients = models.ManyToManyField(Ingredient, through='CocktailIngredient')
    userreview = models.ManyToManyField(authmodels.User, through='Review')
    glass = models.ForeignKey(Glass, blank=True, null=True, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

# (R) CocktailIngredient: Cocktail-Ingredient
class CocktailIngredient(models.Model):
    class Meta:
        constraints = [
            # Ensure there is only one entry per cocktail-ingredient combination
            UniqueConstraint(fields=['cocktail', 'ingredient'], name='unique_cocktailingredients'),
            # Ensure no cocktail has multiple ingredients in the same position
            UniqueConstraint(fields=['cocktail', 'position'], name='unique_cocktailposition')
        ]
    measurement = models.IntegerField(
        choices=(
            (0, 'ml'),
            (1, 'oz'),
            (2, 'cup'),
            (3, 'tsp'),
            (4, 'Tbsp'),
            (5, 'package'))
        )
    amount = models.FloatField()
    position = models.SmallIntegerField(blank=True, null=True)
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.cocktail}-{self.ingredient}"

# (R) Review: User-Cocktail
class Review(models.Model):
    class Meta:
        constraints = [
            # Ensure that a review is only created once and then updated if necessary
            UniqueConstraint(fields=['user', 'cocktail'], name='unique_review')
        ]
    user = models.ForeignKey(authmodels.User, on_delete=models.CASCADE)
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    likes = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.user}-{self.cocktail}"
