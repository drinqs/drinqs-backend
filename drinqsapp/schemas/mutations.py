import graphene
import graphql_jwt
from drinqsapp.schemas.queries import Users
from django.contrib.auth import models as authmodels

class UserMutation(graphene.Mutation):
    class Arguments:
      # The input arguments for this mutation
      username = graphene.String(required=True)
      email = graphene.String(required=True)
      password = graphene.String(required=True)
      firstname = graphene.String()
      lastname = graphene.String()


    # The class attributes define the response of the mutation
    user = graphene.Field(Users)

    @classmethod
    def mutate(cls, root, info, username, email, password, firstname, lastname):
        user = authmodels.User.objects.create_user(username, email, password)
        user.first_name = firstname
        user.lastname = lastname
        user.save()
        # Notice we return an instance of this mutation
        return UserMutation(user=user)

class Mutation(graphene.ObjectType):
  token_auth = graphql_jwt.ObtainJSONWebToken.Field()
  verify_token = graphql_jwt.Verify.Field()
  refresh_token = graphql_jwt.Refresh.Field()
  revoke_token = graphql_jwt.Revoke.Field()

  create_user = UserMutation.Field()

  # create user

  # like cocktail (drinq it)

  # reviews

  # settings
