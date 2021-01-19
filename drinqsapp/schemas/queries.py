
from graphene_django import DjangoObjectType
import graphene
from graphene import List, Field
from graphql_jwt.decorators import login_required, staff_member_required

# Import models
import drinqsapp.models as models
from django.contrib.auth import models as authmodels

class CocktailIngredient(DjangoObjectType):
    class Meta:
        model = models.CocktailIngredient
        fields = ('id', 'measurement', 'amount', 'position', 'cocktail', 'ingredient')

class Cocktail(DjangoObjectType):
    class Meta:
        model = models.Cocktail
        fields = ('id', 'name', 'alcoholic', 'category', 'glass', 'ingredients', 'preparation', 'thumbnail_url', 'reviews')

    cocktail_ingredients = List(CocktailIngredient)
    def resolve_cocktail_ingredients(parent, info):
        return models.CocktailIngredient.objects.filter(cocktail_id=parent.id)

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
    cocktails = graphene.List(Cocktail, alcoholic=graphene.String(), category=graphene.String(), glass=graphene.String())
    next_cocktail = graphene.Field(Cocktail)
    me = graphene.Field(User)
    reviews = graphene.List(Review, username=graphene.String(), cocktail=graphene.String(), likes=graphene.Boolean())

    @login_required
    def resolve_cocktails(self, info, **args):
        if args.get('glass'):
            args['glass'] = models.Glass.objects.get(name=args.get('glass')).id

        try:
            return models.Cocktail.objects.filter(**args)
        except models.Cocktail.DoesNotExist:
            return None

    @login_required
    def resolve_next_cocktail(self, info):
        try:
            return models.Cocktail.objects.get(pk=1)
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
