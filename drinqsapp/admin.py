from django.contrib import admin

# TODO
# Remove for production
from .models import Cocktail, Glass, Ingredient, IngredientType, CocktailHasIngredient, Reviewed, Characteristic

# Register your models here.

# Just for manual administration of database
# TODO
# Remove for production
admin.site.register(Cocktail)
admin.site.register(Glass)
admin.site.register(Ingredient)
admin.site.register(IngredientType)
admin.site.register(CocktailHasIngredient)
admin.site.register(Reviewed)
admin.site.register(Characteristic)