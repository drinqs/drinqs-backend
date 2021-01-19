import graphene
import graphql_jwt
from drinqsapp.schemas.queries import User, Error
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
    user = graphene.Field(User)
    errors = graphene.List(Error)

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

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    create_user = UserMutation.Field()

    # create user

    # like cocktail (drinq it)

    # reviews

    # settings
