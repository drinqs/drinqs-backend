import graphene
import graphql_jwt

import drinqsapp.graphql.mutations as mutations

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()

    create_user = mutations.UserMutation.Field()
    update_profile = mutations.ProfileMutation.Field()
    complete_onboarding = mutations.OnboardingCompleteMutation.Field()

    review = mutations.ReviewMutation.Field()
