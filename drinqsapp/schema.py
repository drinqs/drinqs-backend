import graphene
import drinqsapp.schemas.queries
import drinqsapp.schemas.mutations

# Query object for GraphQL API requests
class Query(drinqsapp.schemas.queries.Query, graphene.ObjectType):
    pass

class Mutation(drinqsapp.schemas.mutations.Mutation ,graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
