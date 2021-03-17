from typing import *
from decimal import Decimal
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model

from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework import status

from django_basket.rest.serializers import BasketSerializer
from django_basket.models import BaseBasket

from example_apps.products.models import Product
from example_apps.products.basket import create_items
from ..utils import overwrite_settings

User = get_user_model()


class BasketAPITestCase(APITestCase):

    def setUp(self):
        self.username = "user"
        self.email = "user@mail.com"
        self.password = "password"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        # Mock request
        self.request = APIRequestFactory().get("/admin/login/")
        self.request.session = self.client.session
        self.request.user = self.user
        # Products
        self.product1 = Product.objects.create(title="title1", price=1)
        self.product2 = Product.objects.create(title="title2", price=2)
        self.product3 = Product.objects.create(title="title3", price=3)

    def test_receive(self):
        response = self.client.get("/api/basket/receive/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        basket = BaseBasket.objects.first()
        self.assertEqual(response.data, BasketSerializer(basket).data)

    def test_custom_receive_serializer(self):
        response = self.client.get("/api/basket/receive/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        basket = BaseBasket.objects.first()
        self.assertEqual(response.data, BasketSerializer(basket).data)
