from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseNotFound, JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
import json
from json import JSONDecodeError
from .models import Article, Comment
from django.core.exceptions import ObjectDoesNotExist


def signup(request):
    if request.method == 'POST':
        try:
            req_data = json.loads(request.body.decode())
            username = req_data['username']
            password = req_data['password']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        User.objects.create_user(username=username, password=password)
        return HttpResponse(status=201)

    else:
        return HttpResponseNotAllowed(['POST'])


def signin(request):
    if request.method == 'POST':
        try:
            req_data = json.loads(request.body.decode())
            username = req_data['username']
            password = req_data['password']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=401)

    else:
        return HttpResponseNotAllowed(['POST'])


def signout(request):
    if request.method == 'GET':
        if not_authenticated(request): return HttpResponse(status=401)
        logout(request)
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])


def article(request):
    if request.method == 'GET':
        if not_authenticated(request): return HttpResponse(status=401)
        article_list = [{'title': article['title'], 'content': article['content'], 'author': article['author_id']} for
                        article in Article.objects.all().values('title', 'content', 'author_id')]
        return JsonResponse(article_list, safe=False)

    elif request.method == 'POST':
        if not_authenticated(request): return HttpResponse(status=401)
        try:
            req_data = json.loads(request.body.decode())
            article_title = req_data['title']
            article_content = req_data['content']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()
        article = Article(title=article_title, content=article_content, author=request.user)
        article.save()
        response_dict = {'id': article.id, 'title': article.title, 'content': article.content,
                         'author_id': article.author.id}

        return JsonResponse(response_dict, status=201)
    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


def article_id(request, article_id):
    if request.method == 'GET':
        if not_authenticated(request): return HttpResponse(status=401)

        # 404 : non-existing article
        try:
            article = Article.objects.get(id=article_id)
        except ObjectDoesNotExist as e:
            return HttpResponseNotFound()

        response_dict = {"title": article.title, "content": article.content, "author": article.author.id}
        return JsonResponse(response_dict)

    elif request.method == 'PUT':
        if not_authenticated(request): return HttpResponse(status=401)
        try:
            req_data = json.loads(request.body.decode())
            new_article_title = req_data['title']
            new_article_content = req_data['content']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()

        # 404 : non-existing article
        try:
            article = Article.objects.get(id=article_id)
        except ObjectDoesNotExist as e:
            return HttpResponseNotFound()
        # 403 : non-author
        if not article.author.id == request.user.id:
            return HttpResponseForbidden()

        article.title = new_article_title
        article.content = new_article_content
        article.save()

        response_dict = {'id': article.id, 'title': article.title, 'content': article.content,
                         'author_id': article.author.id}
        return JsonResponse(response_dict, status=200)

    elif request.method == 'DELETE':
        if not_authenticated(request): return HttpResponse(status=401)

        # 404 : non-existing article
        try:
            article = Article.objects.get(id=article_id)
        except ObjectDoesNotExist as e:
            return HttpResponseNotFound()
        # 403 : non-author
        if not article.author.id == request.user.id:
            return HttpResponseForbidden()

        article.delete()
        return HttpResponse(status=200)

    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


def article_id_comment(request, article_id):
    if request.method == 'GET':
        if not_authenticated(request): return HttpResponse(status=401)

        # 404 : non-existing article
        try:
            article = Article.objects.get(id=article_id)
        except ObjectDoesNotExist as e:
            return HttpResponseNotFound()

        comment_list = [{"article": comment["article_id"], "content": comment["content"], "author": comment["author_id"]} for comment in article.comments.values()]
        return JsonResponse(comment_list, safe=False)

    elif request.method == 'POST':
        if not_authenticated(request): return HttpResponse(status=401)
        try:
            req_data = json.loads(request.body.decode())
            comment_content = req_data['content']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()

        # 404 : non-existing article
        try:
            article = Article.objects.get(id=article_id)
        except ObjectDoesNotExist as e:
            return HttpResponseNotFound()

        comment = Comment(content=comment_content, article=article, author=request.user)
        comment.save()
        response_dict = {'id': comment.id, 'article_id': comment.article.id, 'content': comment.content,
                         'author_id': comment.author.id}

        return JsonResponse(response_dict, status=201)

    else:
        return HttpResponseNotAllowed(['GET', 'POST'])


def comment_id(request, comment_id):
    if request.method == 'GET':
        if not_authenticated(request): return HttpResponse(status=401)

        # 404 : non-existing comment
        try:
            comment = Comment.objects.get(id=comment_id)
        except ObjectDoesNotExist as e:
            return HttpResponseNotFound()

        response_dict = {"article": comment.article_id, "content": comment.content, "author": comment.author_id}
        return JsonResponse(response_dict)

    elif request.method == 'PUT':
        if not_authenticated(request): return HttpResponse(status=401)
        try:
            req_data = json.loads(request.body.decode())
            new_comment_content = req_data['content']
        except (KeyError, JSONDecodeError) as e:
            return HttpResponseBadRequest()

        # 404 : non-existing comment
        try:
            comment = Comment.objects.get(id=comment_id)
        except ObjectDoesNotExist as e:
            return HttpResponseNotFound()
        # 403 : non-author
        if not comment.author.id == request.user.id:
            return HttpResponseForbidden()

        comment.content = new_comment_content
        comment.save()

        response_dict = {'id': comment.id, 'article_id': comment.article_id, 'content': comment.content,
                         'author_id': comment.author.id}
        return JsonResponse(response_dict, status=200)

    elif request.method == 'DELETE':
        if not_authenticated(request): return HttpResponse(status=401)

        # 404 : non-existing comment
        try:
            comment = Comment.objects.get(id=comment_id)
        except ObjectDoesNotExist as e:
            return HttpResponseNotFound()
        # 403 : non-author
        if not comment.author.id == request.user.id:
            return HttpResponseForbidden()

        comment.delete()
        return HttpResponse(status=200)

    else:
        return HttpResponseNotAllowed(['GET', 'PUT', 'DELETE'])


@ensure_csrf_cookie
def token(request):
    if request.method == 'GET':
        return HttpResponse(status=204)
    else:
        return HttpResponseNotAllowed(['GET'])


def not_authenticated(request):
    return not request.user.is_authenticated
