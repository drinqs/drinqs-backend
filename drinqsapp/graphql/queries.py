
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required, staff_member_required
import graphene

# TODO: Remove if recommender is implemented and next_cocktail should not deliver random
import random

import drinqsapp.graphql.types as types
import drinqsapp.models as models
from django.contrib.auth import models as authmodels

class Query(graphene.ObjectType):
    cocktails = graphene.List(
        types.Cocktail,
        alcoholic=graphene.Boolean(),
        category=graphene.String(),
        glass=graphene.String(),
    )
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

    next_cocktail = graphene.Field(types.Cocktail)
    @login_required
    def resolve_next_cocktail(self, info):
        try:
            cocktail_ids = models.Cocktail.objects.filter().values('id')
            cocktail_id = random.choice(cocktail_ids)["id"]

            return models.Cocktail.objects.get(pk=cocktail_id)
        except models.Cocktail.DoesNotExist:
            return None

    me = graphene.Field(types.User)
    @login_required
    def resolve_me(self, info):
        print(info.context.user.id)
        try:
            return authmodels.User.objects.get(pk=info.context.user.id)
        except authmodels.User.DoesNotExist:
            return None

    reviews = graphene.List(
        types.Review,
        username=graphene.String(),
        cocktail=graphene.String(),
        liked=graphene.Boolean(),
    )
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
