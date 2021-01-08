
from graphene_django import DjangoObjectType
import graphene
from graphene import List, Field
from graphql_jwt.decorators import login_required

# Import models
from drinqsapp.models import Cocktail, Glass, Ingredient, IngredientTag, CocktailIngredients, Review
from django.contrib.auth import models as authmodels

class Recipes(DjangoObjectType):
    class Meta:
        model = CocktailIngredients
        fields = ('id', 'measurement', 'amount', 'position', 'cocktail', 'ingredient')

class Cocktails(DjangoObjectType):
    class Meta:
        model = Cocktail
        fields = ('id', 'name', 'alcoholic', 'category', 'glass', 'ingredients', 'preparation', 'thumbnailurl', 'userreview')

    cocktail_ingredients = List(Recipes)

    def resolve_cocktail_ingredients(parent, info):
        return CocktailIngredients.objects.filter(cocktail_id=parent.id)

class Glasses(DjangoObjectType):
    class Meta:
        model = Glass
        fields = ('id', 'name')

class Ingredients(DjangoObjectType):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'ingredienttag')

class IngredientTags(DjangoObjectType):
    class Meta:
        model = IngredientTag
        fields = ('id', 'name', 'user')

class Reviews(DjangoObjectType):
    class Meta:
        model = Review
        fields = ('id', 'user', 'cocktail', 'likes')

class Users(DjangoObjectType):
    class Meta:
        model = authmodels.User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class Query(graphene.ObjectType):
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

    @login_required
    def resolve_cocktails(self, info, **args):
        if args.get('glass'):
            args['glass'] = Glass.objects.get(name=args.get('glass')).id

        try:
            return Cocktail.objects.filter(**args)
        except Cocktail.DoesNotExist:
            return None

    @login_required
    def resolve_glasses(self, info):
        return Glass.objects.all()

    @login_required
    def resolve_ingredients(self, info):
        return Ingredient.objects.all()

    @login_required
    def resolve_ingredienttags(self, info):
        return IngredientTag.objects.all()

    @login_required
    def resolve_users(self, info):
        return authmodels.User.objects.all()

    @login_required
    def resolve_recipes(self, info):
        return CocktailIngredients.objects.all()

    @login_required
    def resolve_recipe(self, info, cocktailid):
        # c_id = Cocktail.objects.get(name=cocktail).id
        try:
            return CocktailIngredients.objects.filter(cocktail_id=cocktailid)
        except CocktailIngredients.DoesNotExist:
            return None

    @login_required
    def resolve_nextcocktail(self, info):
        try:
            return Cocktail.objects.get(pk=1)
        except Cocktail.DoesNotExist:
            return None

    @login_required
    def resolve_currentuser(self, info):
        print(info.context.user.id)
        try:
            return authmodels.User.objects.get(pk=info.context.user.id)
        except authmodels.User.DoesNotExist:
            return None

    @login_required
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
