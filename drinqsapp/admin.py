from django.contrib import admin

# TODO
# Remove for production
from .models import Cocktail, Glass, Ingredient, IngredientTag, CocktailIngredients, Review

# Register your models here.

# Just for manual administration of database
# TODO
# Remove for production
admin.site.register(Cocktail)
admin.site.register(Glass)
admin.site.register(Ingredient)
admin.site.register(IngredientTag)
admin.site.register(CocktailIngredients)
admin.site.register(Review)