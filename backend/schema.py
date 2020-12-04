import graphene
from graphene_django import DjangoObjectType

# GraphQL API schema

# Import models
from drinqsapp.models import Cocktail, Glass, Ingredient, CocktailHasIngredient, Reviewed, Characteristic
from drinqsapp.models import IngredientType as IngredientCategory

class CocktailType(DjangoObjectType):
    class Meta:
        model = Cocktail
        fields = ('id', 'name', 'alcoholic', 'category', 'preparation', 'thumbnailUrl')

class GlassType(DjangoObjectType):
    class Meta:
        model = Glass
        fields = ('id', 'name')

class IngredientType(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'ingredientType_id')

class CocktailHasIngredientType(DjangoObjectType):
    class Meta:
        model = CocktailHasIngredient
        fields = ('id', 'measurement', 'amount', 'position', 'cocktail_id', 'ingredient_id')

class ReviewedType(DjangoObjectType):
    class Meta:
        model = Reviewed
        fields = ('id', 'likes', 'cocktail_id', 'user_id')

class CharacteristicType(DjangoObjectType):
    class Meta:
        model = Characteristic
        fields = ('id', 'name')

class IngredientCategoryType(DjangoObjectType):
    class Meta:
        model = IngredientCategory
        fields = ('id', 'name')

# Query object for GraphQL API requests
class Query(graphene.ObjectType):
    all_cocktails = graphene.List(CocktailType)
    all_glasses = graphene.List(GlassType)
    all_ingredients = graphene.List(IngredientType)
    all_recipes = graphene.List(CocktailHasIngredientType)
    all_reviews = graphene.List(ReviewedType)
    all_characteristics = graphene.List(CharacteristicType)
    all_ingredienttypes = graphene.List(IngredientCategoryType)

    def resolve_all_cocktails(self, info):
        return Cocktail.objects.all()

    def resolve_all_glasses(self, info):
        return Glass.objects.all()
    
    def resolve_all_ingredients(self, info):
        return Ingredient.objects.all()

    def resolve_all_recipes(self, info):
        return CocktailHasIngredient.objects.all()

    def resolve_all_reviews(self, info):
        return Reviewed.objects.all()

    def resolve_all_characteristics(self, info):
        return Characteristic.objects.all()

    def resolve_all_ingredienttypes(self, info):
        return IngredientType.objects.all()
    

schema = graphene.Schema(query=Query)