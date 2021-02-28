"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

# GraphQL imports
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from drinqsapp.schema import schema


# Local imports
from . import views

urlpatterns = [
    path('', admin.site.urls),
    # path for healtcheck (needed for production deployment)
    path('.well-known/health_check', views.healthcheck, name='healthcheck'),
    # path for GraphQL
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True, schema=schema))),
    # REST user paths
    path('api/auth/login', views.token_auth, name='token_auth'),
    path('api/auth/refresh', views.refresh_token, name='refresh_token'),
    path('api/auth/user', views.current_user, name='current_user'),
]
