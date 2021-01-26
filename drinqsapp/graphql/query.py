
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphql_jwt.decorators import login_required, staff_member_required
import graphene

# TODO: Remove if recommender is implemented and next_cocktail should not deliver random
import random

import drinqsapp.graphql.types as types
import drinqsapp.models as models

class Query(graphene.ObjectType):
    cocktails = graphene.List(
        graphene.NonNull(types.Cocktail),
        required=True,
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
            return []

    cocktail = graphene.NonNull(types.Cocktail, slug=graphene.NonNull(graphene.String))
    @login_required
    def resolve_cocktail(self, info, **args):
        return models.Cocktail.objects.get(slug=args['slug'])

    recommended_cocktails = graphene.relay.ConnectionField(types.CocktailConnection)
    @login_required
    def resolve_recommended_cocktails(self, info, **args):
        return models.Cocktail.objects.all()

    next_cocktail = graphene.Field(types.Cocktail)
    @login_required
    def resolve_next_cocktail(self, info):
        try:
            cocktail_ids = models.Cocktail.objects.values_list('id', flat=True)
            cocktail_id = random.choice(cocktail_ids)

            return models.Cocktail.objects.get(pk=cocktail_id)
        except models.Cocktail.DoesNotExist:
            return None

    bookmarks = graphene.relay.ConnectionField(types.CocktailConnection)
    @login_required
    def resolve_bookmarks(self, info, **args):
        return info.context.user.bookmarks()

    me = graphene.NonNull(types.User)
    @login_required
    def resolve_me(self, info):
        return models.User.objects.get(pk=info.context.user.id)

    reviews = graphene.List(
        graphene.NonNull(types.Review),
        required=True,
        username=graphene.String(),
        cocktail=graphene.String(),
        liked=graphene.Boolean(),
    )
    @login_required
    def resolve_reviews(self, info, **args):
        if args.get('username'):
            args['user_id'] = models.User.objects.get(username=args.get('username')).id
            del args['username']

        if args.get('cocktail'):
            args['cocktail_id'] = models.Cocktail.objects.get(name=args.get('cocktail')).id
            del args['cocktail']

        return models.Review.objects.filter(**args)
