import graphene

import drinqsapp.graphql.mutations as mutations

class Mutation(graphene.ObjectType):
    create_user = mutations.UserMutation.Field()
    update_profile = mutations.ProfileMutation.Field()
    complete_onboarding = mutations.OnboardingCompleteMutation.Field()

    review = mutations.ReviewMutation.Field()
