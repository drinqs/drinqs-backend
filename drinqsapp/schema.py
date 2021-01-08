import graphene
import graphql_jwt
import drinqsapp.schemas.queries

# Query object for GraphQL API requests
class Query(drinqsapp.schemas.queries.Query, graphene.ObjectType):
    pass

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    revoke_token = graphql_jwt.Revoke.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
