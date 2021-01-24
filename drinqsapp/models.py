from django.db import models
from django.db.models import UniqueConstraint, Subquery
from django.contrib.auth.models import AbstractUser

from autoslug import AutoSlugField

# Models for drinqs application.
# (E) Entity model
# (R) Relationship model: A-B

# User model (E)
class User(AbstractUser):
    pass

# (E) Glass
class Glass(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

# (E) Ingredient Tag
class IngredientTag(models.Model):
    name = models.CharField(max_length=128, unique=True)
    users = models.ManyToManyField(User, blank=True)

    def __str__(self):
        return self.name

# (E) Ingredient
class Ingredient(models.Model):
    name = models.CharField(max_length=128, unique=True)
    ingredient_tags = models.ManyToManyField(IngredientTag, blank=True)

    def __str__(self):
        return self.name

# (E) Cocktail
class Cocktail(models.Model):
    ALCOHOLIC_CHOICES = (
        (0, 'not available'),
        (1, 'alcoholic'),
        (2, 'non alcoholic'),
    )

    name = models.CharField(max_length=128, unique=True)
    slug = AutoSlugField(populate_from='name', max_length=128, always_update=True, sep='--', unique=True)
    alcoholic = models.IntegerField(blank=True, null=True, choices=ALCOHOLIC_CHOICES)
    category = models.CharField(max_length=128, blank=True, null=True)
    preparation = models.TextField(blank=True, null=True)
    thumbnail_url = models.CharField(max_length=512, blank=True, null=True)
    ingredients = models.ManyToManyField(Ingredient, through='CocktailIngredient')
    reviewers = models.ManyToManyField(User, through='Review')
    glass = models.ForeignKey(Glass, blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

# (R) CocktailIngredient: Cocktail-Ingredient
class CocktailIngredient(models.Model):
    MEASUREMENT_CHOICES = (
        (0, 'ml'),
        (1, 'oz'),
        (2, 'cup'),
        (3, 'tsp'),
        (4, 'Tbsp'),
        (5, 'package'),
    )

    class Meta:
        constraints = [
            # Ensure there is only one entry per cocktail-ingredient combination
            UniqueConstraint(fields=['cocktail', 'ingredient'], name='unique_cocktailingredients'),
            # Ensure no cocktail has multiple ingredients in the same position
            UniqueConstraint(fields=['cocktail', 'position'], name='unique_cocktailposition')
        ]

    measurement = models.IntegerField(choices=MEASUREMENT_CHOICES)
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

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cocktail = models.ForeignKey(Cocktail, on_delete=models.CASCADE)
    liked = models.BooleanField(default=False, null=True)
    bookmarked = models.BooleanField(default=False, null=True)

    def __str__(self):
        return f"{self.user}-{self.cocktail}"
