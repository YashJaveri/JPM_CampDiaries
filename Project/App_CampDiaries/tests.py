import json
from django.contrib.auth.models import User
from rest_framework import status
from .models import *
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

class ProfileTestCase(APITestCase):
    def setUp(self):
        self.user= User.objects.create_user(username="yashj@gmail", password="XYasdasdcdcfZ")
        self.profile = Profile.objects.create(user=self.user)
        self.token = Token.objects.create(user=self.user)
        self.api_authentication()

    def api_authentication(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

    def test_profile_detail_retrieve(self):
        response =self.client.get('profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class CreateCampTestCase(APITestCase):
    def setUp(self):
        self