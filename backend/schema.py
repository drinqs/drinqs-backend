import graphene
from graphene_django import DjangoObjectType

# GraphQL API schema

# Import models
from drinqsapp.models import Cocktail, Glass, Ingredient, IngredientTag, CocktailIngredients, Review

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
        fields = ('id', 'name')

class CocktailIngredientsType(DjangoObjectType):
    class Meta:
        model = CocktailIngredients
        fields = ('id', 'measurement', 'amount', 'position')

class ReviewType(DjangoObjectType):
    class Meta:
        model = Review
        fields = ('id', 'likes')

class IngredientTagType(DjangoObjectType):
    class Meta:
        model = IngredientTag
        fields = ('id', 'name')

# Query object for GraphQL API requests
class Query(graphene.ObjectType):
    all_cocktails = graphene.List(CocktailType)
    all_glasses = graphene.List(GlassType)
    all_ingredients = graphene.List(IngredientType)
    all_recipes = graphene.List(CocktailIngredientsType)
    all_reviews = graphene.List(ReviewType)
    all_ingredienttags = graphene.List(IngredientTagType)

    def resolve_all_cocktails(self, info):
        return Cocktail.objects.all()

    def resolve_all_glasses(self, info):
        return Glass.objects.all()
    
    def resolve_all_ingredients(self, info):
        return Ingredient.objects.all()

    def resolve_all_recipes(self, info):
        return CocktailIngredients.objects.all()

    def resolve_all_reviews(self, info):
        return Review.objects.all()

    def resolve_all_ingredienttypes(self, info):
        return IngredientTag.objects.all()
    

schema = graphene.Schema(query=Query)