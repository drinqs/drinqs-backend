from graphql_jwt.exceptions import JSONWebTokenError
from graphql_jwt.utils import get_payload, get_user_by_payload
from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework import exceptions


class TokenAuthentication(BaseAuthentication):
    keyword = 'JWT'

    def authenticate(self, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0].lower() != self.keyword.lower().encode():
            return None

        if len(auth) == 1:
            msg = 'Invalid token header. No credentials provided.'
            raise exceptions.AuthenticationFailed(msg)
        if len(auth) > 2:
            msg = 'Invalid token header. Token string should not contain spaces.'
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1].decode()
        except UnicodeError as unicode_error:
            msg = 'Invalid token header. Token string should not contain invalid characters.'
            raise exceptions.AuthenticationFailed(msg) from unicode_error

        try:
            payload = get_payload(token)
            user = get_user_by_payload(payload)
        except JSONWebTokenError as exception:
            raise exceptions.AuthenticationFailed(str(exception)) from exception

        if user is None or not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (user, None)

    def authenticate_header(self, _request):
        return self.keyword
