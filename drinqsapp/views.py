from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from graphql_jwt import signals
from graphql_jwt.utils import jwt_payload, jwt_encode
from graphql_jwt.refresh_token import signals as refresh_signals
from graphql_jwt.refresh_token.shortcuts import get_refresh_token, refresh_token_lazy
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from drinqsapp.serializers import UserSerializer
from drinqsapp.authentication import TokenAuthentication

# Create your views here.
def healthcheck(request):
    return HttpResponse("ok")

@api_view(['POST'])
def token_auth(request):
    username = request.data.get('username', '')
    password = request.data.get('password', '')

    user = authenticate(
        request=request,
        username=username,
        password=password,
    )

    if user is None:
        return Response({'error': 'Please enter valid credentials'}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    signals.token_issued.send(sender=None, request=request, user=user)
    payload = jwt_payload(user, request)
    token = jwt_encode(payload, request)
    refresh_token = refresh_token_lazy(user)

    return Response({
        'token': token,
        'refreshToken': refresh_token,
        'payload': payload,
    })

@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refreshToken', '')
    if not refresh_token:
        return Response({'error': 'Refresh token is required'})

    old_refresh_token = get_refresh_token(refresh_token, request)

    if old_refresh_token.is_expired(request):
        return Response({ 'error': 'Refresh token is expired' }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    payload = jwt_payload(
        old_refresh_token.user,
        request,
    )
    token = jwt_encode(payload, request)

    new_refresh_token = refresh_token_lazy(
        old_refresh_token.user,
        old_refresh_token,
    )

    refresh_signals.refresh_token_rotated.send(
        sender=None,
        request=request,
        refresh_token=old_refresh_token,
        refresh_token_issued=new_refresh_token,
    )

    return Response({
        'token': token,
        'refreshToken': new_refresh_token,
        'payload': payload,
    })

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
def current_user(request):
    user = request.user
    if not user or isinstance(user, AnonymousUser):
        return Response({ 'error': 'You are not allowed to see this page' }, status=status.HTTP_401_UNAUTHORIZED)
    return Response({ 'user': UserSerializer(user).data })
