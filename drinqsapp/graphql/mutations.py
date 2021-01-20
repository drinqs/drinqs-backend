import graphene
import graphql_jwt
from graphql_jwt.decorators import login_required, staff_member_required

import drinqsapp.graphql.types as types
import drinqsapp.models as models
from django.contrib.auth import models as authmodels


class UserMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()

    # The class attributes define the response of the mutation
    user = graphene.Field(types.User)
    errors = graphene.List(types.Error)

    @classmethod
    def mutate(cls, root, info, username, email, password, first_name, last_name):
        errors = []
        user = None
        if authmodels.User.objects.filter(username=username).count() > 0:
            errors.append({
                'key': 'username',
                'message': 'Username is already taken'
            })
        if authmodels.User.objects.filter(email=email).count() > 0:
            errors.append({
                'key': 'email',
                'message': 'Email is already taken'
            })
        if not errors:
            user = authmodels.User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Notice we return an instance of this mutation
        return UserMutation(user=user, errors=errors)

class ReviewMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        cocktail_id = graphene.ID(required=True)
        liked = graphene.Boolean()
        bookmarked = graphene.Boolean()

    # The class attributes define the response of the mutation
    review = graphene.Field(types.Review)

    @classmethod
    @login_required
    def mutate(cls, root, info, cocktail_id, **kwargs):
        user_id = info.context.user.id

        try:
            review = models.Review.objects.get(cocktail_id=cocktail_id, user_id=user_id)
        except models.Review.DoesNotExist:
            review = models.Review.objects.create(cocktail_id=cocktail_id, user_id=user_id)

        review.liked = kwargs.get('liked', None)
        review.bookmarked = kwargs.get('bookmarked', None)
        review.save()

        # Notice we return an instance of this mutation
        return ReviewMutation(review=review)

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    create_user = UserMutation.Field()

    review = ReviewMutation.Field()
