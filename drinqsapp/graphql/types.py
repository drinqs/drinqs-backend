from graphene_django import DjangoObjectType
import graphene

import drinqsapp.models as models
from django.contrib.auth import models as authmodels

class Review(DjangoObjectType):
    class Meta:
        model = models.Review
        fields = ('id', 'user', 'cocktail', 'liked', 'bookmarked')

class CocktailIngredient(DjangoObjectType):
    class Meta:
        model = models.CocktailIngredient
        fields = ('id', 'amount', 'position', 'cocktail', 'ingredient')

    measurement = graphene.NonNull(graphene.String)
    def resolve_measurement(self, info):
        value_map = { k: v for k, v in models.CocktailIngredient.MEASUREMENT_CHOICES }

        return value_map[self.measurement]

class Cocktail(DjangoObjectType):
    class Meta:
        model = models.Cocktail
        fields = ('id', 'name', 'slug', 'category', 'glass', 'ingredients', 'preparation', 'thumbnail_url')

    alcoholic = graphene.Boolean(required=False)
    def resolve_alcoholic(self, info):
        value_map = {
            1: True,
            2: False,
        }
        return value_map[self.alcoholic]

    cocktail_ingredients = graphene.List(graphene.NonNull(CocktailIngredient), required=True)
    def resolve_cocktail_ingredients(self, info):
        return models.CocktailIngredient.objects.filter(cocktail_id=self.id)

    like_ratio = graphene.Float()
    def resolve_like_ratio(self, info):
        total_review_count = models.Review.objects.filter(cocktail_id=self.id).exclude(liked=None).count()
        if total_review_count == 0:
            return None

        positive_review_count = models.Review.objects.filter(cocktail_id=self.id, liked=True).count()
        return float(positive_review_count / total_review_count)

    review = graphene.Field(Review)
    def resolve_review(self, info):
        user_id = info.context.user.id
        try:
            return models.Review.objects.get(cocktail_id=self.id, user_id=user_id)
        except models.Review.DoesNotExist:
            return None

class Error(graphene.ObjectType):
    key = graphene.NonNull(graphene.String)
    message = graphene.NonNull(graphene.String)

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

class User(DjangoObjectType):
    class Meta:
        model = authmodels.User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
