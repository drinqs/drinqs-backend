
from graphene_django import DjangoObjectType, DjangoConnectionField
from graphql_jwt.decorators import login_required, staff_member_required
import graphene
from drinqsapp.recommender import utility



import drinqsapp.graphql.types as types
import drinqsapp.models as models

class Query(graphene.ObjectType):
    cocktails = graphene.relay.ConnectionField(types.CocktailConnection)
    @login_required
    def resolve_cocktails(self, info, **args):
        return models.Cocktail.objects.all()

    search = graphene.relay.ConnectionField(types.CocktailConnection, search_term=graphene.String())
    @login_required
    def resolve_search(self, info, **args):
        search_term = args.get('search_term', '')
        if args.get('search_term'):
            del args['search_term']

        return models.Cocktail.objects.search(search_term)

    cocktail = graphene.NonNull(types.Cocktail, slug=graphene.NonNull(graphene.String))
    @login_required
    def resolve_cocktail(self, info, **args):
        return models.Cocktail.objects.get(slug=args['slug'])

    recommended_cocktails = graphene.relay.ConnectionField(types.CocktailConnection)
    @login_required
    def resolve_recommended_cocktails(self, info, **args):
        recommendations = utility.getRecommendationForUser(userID=info.context.user.id, getOnlyFirst=False)
        return recommendations

    next_cocktail = graphene.Field(types.Cocktail)
    @login_required
    def resolve_next_cocktail(self, info):
        try:
            recommendation = utility.getRecommendationForUser(userID=info.context.user.id, getOnlyFirst=True)
            return recommendation
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
