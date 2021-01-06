from django.shortcuts import render
from django.http import HttpResponse, JsonResponse

# Create your views here.
def healthcheck(request):
    return HttpResponse("ok")
