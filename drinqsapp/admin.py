from django.contrib import admin

from .models import Cocktail, Glass, Ingredient, IngredientTag, CocktailIngredient, Review, User

# Register your models here.

# Just for manual administration of database
admin.site.register(Cocktail)
admin.site.register(Glass)
admin.site.register(Ingredient)
admin.site.register(IngredientTag)
admin.site.register(CocktailIngredient)
admin.site.register(Review)
admin.site.register(User)
