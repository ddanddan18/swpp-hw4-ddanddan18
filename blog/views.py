from django.http import HttpResponse, HttpResponseNotAllowed
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
import json


def signup(request):
    if request.method == 'POST':
        req_data = json.loads(request.body.decode())
        username = req_data['username']
        password = req_data['password']
        User.objects.create_user(username, password)
        return HttpResponse(status=201)
    else:
        return HttpResponseNotAllowed(['POST'])


@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])


def signin(request):
    return


def signout(request):
    return


def article(request):
    return


def article_id(request):
    return


def comment_id(request):
    return
