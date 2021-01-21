import graphene
import drinqsapp.graphql.query
import drinqsapp.graphql.mutation

class Query(drinqsapp.graphql.query.Query, graphene.ObjectType):
    pass

class Mutation(drinqsapp.graphql.mutation.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
