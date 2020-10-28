from django.test import TestCase, Client
import json
from .models import Article, Comment
from django.contrib.auth.models import User


class BlogTestCase(TestCase):
    dump_user = json.dumps({'username': 'chris', 'password': 'chris'})
    dump_article = json.dumps({'title': 'my tmi', 'content': 'i did hw hard'})
    dump_comment = json.dumps({'content': 'there is no one asked'})

    def setUp(self):
        # Article.objects.create(title="title1", content="content1", author= )
        return

    @staticmethod
    def get_csrf(client):
        response = client.get('/api/token/')
        return response.cookies['csrftoken'].value

    def signup(self, client, csrftoken):
        path = '/api/signup/'
        response = client.post(path, self.dump_user,
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection

    def signin(self, client, csrftoken):
        path = '/api/signin/'
        response = client.post(path, self.dump_user, content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 204)

    def test_csrf(self):
        # By default, csrf checks are disabled in test client
        # To test csrf protection we enforce csrf checks here
        client = Client(enforce_csrf_checks=True)
        response = client.post('/api/signup/', self.dump_user,
                               content_type='application/json')
        self.assertEqual(response.status_code, 403)  # Request without csrf token returns 403 response

        response = client.get('/api/token/')
        csrftoken = response.cookies['csrftoken'].value  # Get csrf token from cookie

        response = client.post('/api/signup/', self.dump_user,
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection

        response = client.delete('/api/token/', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

    def test_signup(self):
        client = Client(enforce_csrf_checks=True)
        csrftoken = self.get_csrf(client)
        path = '/api/signup/'

        # 405 test
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        # 400 test
        response = client.post(path, json.dumps({}), content_type='application/json',
                               HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

        # 201 test (request successfully)
        response = client.post(path, self.dump_user,
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection

    def test_signin(self):
        client = Client(enforce_csrf_checks=True)
        csrftoken = self.get_csrf(client)
        path = '/api/signin/'

        # 405 test
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        # 400 test
        response = client.post(path, json.dumps({}), content_type='application/json',
                               HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

        # 401 test (before login)
        response = client.post(path, self.dump_user,
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)  # Pass csrf protection

        # 204 test (request successfully)
        self.signup(client, csrftoken)
        response = client.post(path, self.dump_user,
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 204)  # Pass csrf protection

    def test_signout(self):
        client = Client(enforce_csrf_checks=True)
        csrftoken = self.get_csrf(client)
        path = '/api/signout/'

        # 405 test
        response = client.post(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.put(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.delete(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        # 401 test (before login)
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)  # Pass csrf protection

        # 204 test (request successfully)
        self.signup(client, csrftoken)
        self.signin(client, csrftoken)
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 204)  # Pass csrf protection

    def test_article(self):
        client = Client(enforce_csrf_checks=True)
        csrftoken = self.get_csrf(client)
        path = '/api/article/'

        # 405 test (PUT, DELETE)
        response = client.put(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.delete(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        # 401 test (GET, POST before login)
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.post(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)

        # authenticate
        self.signup(client, csrftoken)
        self.signin(client, csrftoken)
        csrftoken = self.get_csrf(client)

        # 400 test (POST)
        response = client.post(path, json.dumps({}), content_type='application/json',
                               HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

        # 200, 201 test (request successfully)
        ## GET
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  # Pass csrf protection

        ## POST
        response = client.post(path, self.dump_article,
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection

    def test_article_id(self):
        client = Client(enforce_csrf_checks=True)
        csrftoken = self.get_csrf(client)
        article_id = 1
        path = '/api/article/{}/'.format(article_id)

        # 405 test (POST)
        response = client.post(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        # 401 test (GET, PUT, DELETE before login)
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.put(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.delete(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)

        # authenticate
        self.signup(client, csrftoken)
        self.signin(client, csrftoken)
        csrftoken = self.get_csrf(client)

        # 404 test (GET, PUT, DELETE on empty article DB)
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.put(path, data=self.dump_article, content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.delete(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)

        Article.objects.create(title="testtitle", content="testcontent", author=User.objects.get(id=1))
        # 400 test (PUT)
        response = client.put(path, json.dumps({}), content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

        # 403 test
        other_user = User.objects.create_user(username="swpp", password="iluvswpp")
        other_user_article = Article.objects.create(title="testtitle", content="testcontent", author=other_user)
        other_article_path = '/api/article/{}/'.format(other_user_article.id)

        response = client.put(other_article_path, data=self.dump_article, content_type='application/json',
                              HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 403)
        response = client.delete(other_article_path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 403)

        # 200 test (request successfully)
        ## GET
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  # Pass csrf protection

        ## PUT
        response = client.put(path, self.dump_article,
                              content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  # Pass csrf protection

        ## DELETE
        response = client.delete(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  # Pass csrf protection

    def test_article_id_comment(self):
        client = Client(enforce_csrf_checks=True)
        csrftoken = self.get_csrf(client)
        article_id = 1
        path = '/api/article/{}/comment/'.format(article_id)

        # 405 test (PUT, DELETE)
        response = client.put(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)
        response = client.delete(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        # 401 test (GET, POST before login)
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.post(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)

        # authenticate
        self.signup(client, csrftoken)
        self.signin(client, csrftoken)
        csrftoken = self.get_csrf(client)

        # 404 test (GET, POST on empty article DB)
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.post(path, data=self.dump_comment, content_type='application/json',
                               HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)

        # create the article
        Article.objects.create(title="testtitle", content="testcontent", author=User.objects.get(id=1))

        # 400 test (POST)
        response = client.post(path, json.dumps({}), content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

        # 200, 201 test (request successfully)
        ## GET
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  # Pass csrf protection

        ## POST
        response = client.post(path, self.dump_comment,
                               content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 201)  # Pass csrf protection

    def test_comment_id(self):
        client = Client(enforce_csrf_checks=True)
        csrftoken = self.get_csrf(client)
        comment_id = 1
        path = '/api/comment/{}/'.format(comment_id)

        # 405 test (POST)
        response = client.post(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 405)

        # 401 test (GET, PUT, DELETE before login)
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.put(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)
        response = client.delete(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 401)

        # authenticate
        self.signup(client, csrftoken)
        user = User.objects.get(id=1)
        self.signin(client, csrftoken)
        csrftoken = self.get_csrf(client)

        # 404 test (GET, PUT, DELETE on empty comment DB)
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.put(path, data=self.dump_comment, content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)
        response = client.delete(path, data=None, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 404)

        # create the article and the comment
        article = Article.objects.create(title="testtitle", content="testcontent", author=user)
        comment = Comment.objects.create(content="testcomment", article=article, author=user)

        # 400 test (PUT)
        response = client.put(path, json.dumps({}), content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 400)

        # 403 test
        other_user = User.objects.create_user(username="swpp", password="iluvswpp")
        other_user_comment = Comment.objects.create(content="testcontent", article=article, author=other_user)
        other_comment_path = '/api/comment/{}/'.format(other_user_comment.id)

        response = client.put(other_comment_path, data=self.dump_comment, content_type='application/json',
                              HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 403)
        response = client.delete(other_comment_path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 403)

        # 200 test (request successfully)
        ## GET
        response = client.get(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  # Pass csrf protection

        ## PUT
        response = client.put(path, self.dump_comment,
                              content_type='application/json', HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  # Pass csrf protection

        ## DELETE
        response = client.delete(path, HTTP_X_CSRFTOKEN=csrftoken)
        self.assertEqual(response.status_code, 200)  # Pass csrf protection
