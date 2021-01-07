import graphene
import drinqsapp.schemas.queries

# Query object for GraphQL API requests
class Query(drinqsapp.schemas.queries.Query, graphene.ObjectType):
    pass

# class Mutation(graphene.ObjectType):
#     pass

schema = graphene.Schema(query=Query) #, mutation=Mutation)
