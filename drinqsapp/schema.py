from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay, ObjectType
import graphene

# Import models
from drinqsapp.models import Cocktail, Glass, Ingredient, IngredientTag, CocktailIngredients, Review
from django.contrib.auth import models as authmodels

class Cocktails(DjangoObjectType):
    class Meta:
        model = Cocktail
        filter_fields = ['id', 'name', 'alcoholic', 'category', 'glass', 'ingredients', 'userreview']
        interfaces = (relay.Node, )

class Glasses(DjangoObjectType):
    class Meta:
        model = Glass
        filter_fields = ['id', 'name']
        interfaces = (relay.Node, )

class Ingredients(DjangoObjectType):
    class Meta:
        model = Ingredient
        filter_fields = ['id', 'name', 'ingredienttag']
        interfaces = (relay.Node, )

class IngredientTags(DjangoObjectType):
    class Meta:
        model = IngredientTag
        filter_fields = ['id', 'name', 'user']
        interfaces = (relay.Node, )

class Reviews(DjangoObjectType):
    class Meta:
        model = Review
        filter_fields = ['id', 'user', 'cocktail', 'likes']
        interfaces = (relay.Node, )

class Users(DjangoObjectType):
    class Meta:
        model = authmodels.User
        filter_fields = ['id', 'username']
        interfaces = (relay.Node, )

class Recipes(DjangoObjectType):
    class Meta:
        model = CocktailIngredients
        filter_fields = ['id', 'cocktail', 'ingredient']
        interfaces = (relay.Node, )

# Query object for GraphQL API requests
class Query(graphene.ObjectType):
    cocktails = DjangoFilterConnectionField(Cocktails)
    glasses = DjangoFilterConnectionField(Glasses)
    ingredients = DjangoFilterConnectionField(Ingredients)
    ingredienttags = DjangoFilterConnectionField(IngredientTags)
    reviews = DjangoFilterConnectionField(Reviews)
    users = DjangoFilterConnectionField(Users)
    recipes = DjangoFilterConnectionField(Recipes)


schema = graphene.Schema(query=Query)