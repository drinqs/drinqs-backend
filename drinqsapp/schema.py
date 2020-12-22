from graphene_django import DjangoObjectType
# from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay, ObjectType
import graphene

# Import models
from drinqsapp.models import Cocktail, Glass, Ingredient, IngredientTag, CocktailIngredients, Review
from django.contrib.auth import models as authmodels

class Cocktails(DjangoObjectType):
    class Meta:
        model = Cocktail
        fields = ('id', 'name', 'alcoholic', 'category', 'glass', 'ingredients', 'preparation', 'thumbnailurl', 'userreview')
        # filter_fields = ['id', 'name', 'alcoholic', 'category', 'glass', 'ingredients', 'userreview']
        # interfaces = (relay.Node, )

class Glasses(DjangoObjectType):
    class Meta:
        model = Glass
        fields = ('id', 'name')
        # filter_fields = ['id', 'name']
        # interfaces = (relay.Node, )

class Ingredients(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'ingredienttag')
        # filter_fields = ['id', 'name', 'ingredienttag']
        # interfaces = (relay.Node, )

class IngredientTags(DjangoObjectType):
    class Meta:
        model = IngredientTag
        fields = ('id', 'name', 'user')
        # filter_fields = ['id', 'name', 'user']
        # interfaces = (relay.Node, )

class Reviews(DjangoObjectType):
    class Meta:
        model = Review
        fields = ('id', 'user', 'cocktail', 'likes')
        # filter_fields = ['id', 'user', 'cocktail', 'likes']
        # interfaces = (relay.Node, )

class Users(DjangoObjectType):
    class Meta:
        model = authmodels.User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        # filter_fields = ['id', 'username']
        # interfaces = (relay.Node, )

class Recipes(DjangoObjectType):
    class Meta:
        model = CocktailIngredients
        fields = ('id', 'measurement', 'amount', 'position', 'cocktail', 'ingredient')
        # filter_fields = ['id', 'cocktail', 'ingredient']
        # interfaces = (relay.Node, )

# Query object for GraphQL API requests
class Query(graphene.ObjectType):
    # cocktails = DjangoFilterConnectionField(Cocktails)
    # glasses = DjangoFilterConnectionField(Glasses)
    # ingredients = DjangoFilterConnectionField(Ingredients)
    # ingredienttags = DjangoFilterConnectionField(IngredientTags)
    # reviews = DjangoFilterConnectionField(Reviews)
    # users = DjangoFilterConnectionField(Users)
    # recipes = DjangoFilterConnectionField(Recipes)

    glasses = graphene.List(Glasses)
    ingredients = graphene.List(Ingredients)
    ingredienttags = graphene.List(IngredientTags)
    users = graphene.List(Users)
    recipes = graphene.List(Recipes)

    cocktails = graphene.List(Cocktails, alcoholic=graphene.String(), category=graphene.String(), glass=graphene.String())
    recipe = graphene.List(Recipes, cocktailid=graphene.Int(required=True))
    nextcocktail = graphene.Field(Cocktails)
    currentuser = graphene.Field(Users)
    reviews = graphene.List(Reviews, username=graphene.String(), cocktail = graphene.String(), likes=graphene.Boolean())

    def resolve_cocktails(self, info, **args):
        if args.get('glass'):
            args['glass'] = Glass.objects.get(name=args.get('glass')).id
        
        try:
            return Cocktail.objects.filter(**args)
        except Cocktail.DoesNotExist:
            return None

    def resolve_glasses(self, info):
        return Glass.objects.all()

    def resolve_ingredients(self, info):
        return Ingredient.objects.all()
    
    def resolve_ingredienttags(self, info):
        return IngredientTag.objects.all()

    def resolve_users(self, info):
        return authmodels.User.objects.all()

    def resolve_recipes(self, info):
        return CocktailIngredients.objects.all()
    
    def resolve_recipe(self, info, cocktailid):
        # c_id = Cocktail.objects.get(name=cocktail).id
        try:
            return CocktailIngredients.objects.filter(cocktail_id=cocktailid)
        except CocktailIngredients.DoesNotExist:
            return None

    def resolve_nextcocktail(self, info):
        try:
            return Cocktail.objects.get(pk=1)
        except Cocktail.DoesNotExist:
            return None

    def resolve_currentuser(self, info):
        try:
            return authmodels.User.objects.get(pk=1)
        except authmodels.User.DoesNotExist:
            return None

    def resolve_reviews(self, info, **args):
        if args.get('username'):
            args['user_id'] = authmodels.User.objects.get(username=args.get('username')).id
            del args['username']

        if args.get('cocktail'):
            args['cocktail_id'] = Cocktail.objects.get(name=args.get('cocktail')).id
            del args['cocktail']
            
        try:
            return Review.objects.filter(**args)
        except Review.DoesNotExist:
            return None

schema = graphene.Schema(query=Query)