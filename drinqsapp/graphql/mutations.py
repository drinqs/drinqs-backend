import graphene
from graphql_jwt.decorators import login_required, staff_member_required
import copy
import threading
import drinqsapp.graphql.types as types
import drinqsapp.models as models
from drinqsapp.recommender import utility

class UserMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        username = graphene.String(required=True)
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()

    # The class attributes define the response of the mutation
    user = graphene.NonNull(types.User)
    errors = graphene.List(graphene.NonNull(types.Error), required=True)

    @classmethod
    def mutate(cls, root, info, username, email, password, first_name, last_name):
        errors = []
        user = None
        if models.User.objects.filter(username=username).count() > 0:
            errors.append({
                'key': 'username',
                'message': 'Username is already taken'
            })
        if models.User.objects.filter(email=email).count() > 0:
            errors.append({
                'key': 'email',
                'message': 'Email is already taken'
            })
        if not errors:
            user = models.User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

        # Notice we return an instance of this mutation
        return UserMutation(user=user, errors=errors)

class ProfileMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()

    # The class attributes define the response of the mutation
    user = graphene.NonNull(types.User)
    errors = graphene.List(graphene.NonNull(types.Error), required=True)

    @classmethod
    @login_required
    def mutate(cls, root, info, **kwargs):

        errors = []
        user = info.context.user

        username = kwargs.get('username', None)
        if username:
            if models.User.objects.filter(username=username).exclude(id=user.id).count() > 0:
                errors.append({
                    'key': 'username',
                    'message': 'Username is already taken'
                })

        email = kwargs.get('email', None)
        if email:
            if models.User.objects.filter(email=email).exclude(id=user.id).count() > 0:
                errors.append({
                    'key': 'email',
                    'message': 'Email is already taken'
                })

        if not errors:
            user.set_password(kwargs.get('password', user.password))
            user.username = kwargs.get('username', user.username)
            user.email = kwargs.get('email', user.email)
            user.first_name = kwargs.get('first_name', user.first_name)
            user.last_name = kwargs.get('last_name', user.last_name)
            user.save()

        # Notice we return an instance of this mutation
        return ProfileMutation(user=user, errors=errors)

class ReviewMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        cocktail_id = graphene.ID(required=True)
        liked = graphene.Boolean()
        bookmarked = graphene.Boolean()

    # The class attributes define the response of the mutation
    review = graphene.NonNull(types.Review)

    @classmethod
    @login_required
    def mutate(cls, root, info, cocktail_id, **kwargs):
        user_id = info.context.user.id
        oldReview = None
        try:
            review = models.Review.objects.get(cocktail_id=cocktail_id, user_id=user_id)
            oldReview = copy.copy(review)
        except models.Review.DoesNotExist:
            review = models.Review.objects.create(cocktail_id=cocktail_id, user_id=user_id)

        review.liked = kwargs.get('liked', None)
        review.bookmarked = kwargs.get('bookmarked', False)
        review.save()

        t1 = threading.Thread(target=utility.updateCachedUserRecOnMutate, args=(user_id, review, oldReview))
        t1.start()

        # Notice we return an instance of this mutation
        return ReviewMutation(review=review)
