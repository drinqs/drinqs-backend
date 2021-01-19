
from graphene_django import DjangoObjectType
import graphene
from graphene import List, Field
from graphql_jwt.decorators import login_required, staff_member_required

# Import models
import drinqsapp.models as models
from django.contrib.auth import models as authmodels

# TODO:
# Remove if recommender is implemented and next_cocktail should not deliver random
import random

class CocktailIngredient(DjangoObjectType):
    class Meta:
        model = models.CocktailIngredient
        fields = ('id', 'amount', 'position', 'cocktail', 'ingredient')

    measurement = graphene.String()
    def resolve_measurement(self, info):
        value_map = { k: v for k, v in models.CocktailIngredient.MEASUREMENT_CHOICES }

        return value_map[self.measurement]

class Cocktail(DjangoObjectType):
    class Meta:
        model = models.Cocktail
        fields = ('id', 'name', 'category', 'glass', 'ingredients', 'preparation', 'thumbnail_url', 'reviews')

    alcoholic = graphene.Boolean(required=False)
    def resolve_alcoholic(self, info):
        value_map = {
            1: True,
            2: False,
        }

        return value_map[self.alcoholic]

    cocktail_ingredients = List(CocktailIngredient)
    def resolve_cocktail_ingredients(self, info):
        return models.CocktailIngredient.objects.filter(cocktail_id=self.id)

class Glass(DjangoObjectType):
    class Meta:
        model = models.Glass
        fields = ('id', 'name')

class Ingredient(DjangoObjectType):
    class Meta:
        model = models.Ingredient
        fields = ('id', 'name', 'ingredient_tags')

class IngredientTag(DjangoObjectType):
    class Meta:
        model = models.IngredientTag
        fields = ('id', 'name')

class Review(DjangoObjectType):
    class Meta:
        model = models.Review
        fields = ('id', 'user', 'cocktail', 'liked')

class User(DjangoObjectType):
    class Meta:
        model = authmodels.User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')

class Error(graphene.ObjectType):
    key = graphene.NonNull(graphene.String)
    message = graphene.NonNull(graphene.String)

class Query(graphene.ObjectType):
    cocktails = graphene.List(Cocktail, alcoholic=graphene.Boolean(), category=graphene.String(), glass=graphene.String())
    next_cocktail = graphene.Field(Cocktail)
    me = graphene.Field(User)
    reviews = graphene.List(Review, username=graphene.String(), cocktail=graphene.String(), likes=graphene.Boolean())

    @login_required
    def resolve_cocktails(self, info, **args):
        if args.get('glass'):
            args['glass'] = models.Glass.objects.get(name=args.get('glass')).id
        if args.get('alcoholic'):
            if args['alcoholic'] == None:
                args['alcoholic'] = 0
            elif args['alcoholic'] == True:
                args['alcoholic'] = 1
            else:
                args['alcoholic'] = 2

        try:
            return models.Cocktail.objects.filter(**args)
        except models.Cocktail.DoesNotExist:
            return None

    @login_required
    def resolve_next_cocktail(self, info):
        try:
            cocktail_ids = models.Cocktail.objects.filter().values('id')
            cocktail_id = random.choice(cocktail_ids)["id"]

            return models.Cocktail.objects.get(pk=cocktail_id)
        except models.Cocktail.DoesNotExist:
            return None

    @login_required
    def resolve_me(self, info):
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
            args['cocktail_id'] = models.Cocktail.objects.get(name=args.get('cocktail')).id
            del args['cocktail']

        try:
            return models.Review.objects.filter(**args)
        except models.Review.DoesNotExist:
            return None
