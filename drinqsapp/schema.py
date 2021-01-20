import graphene
import drinqsapp.graphql.queries
import drinqsapp.graphql.mutations

class Query(drinqsapp.graphql.queries.Query, graphene.ObjectType):
    pass

class Mutation(drinqsapp.graphql.mutations.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
