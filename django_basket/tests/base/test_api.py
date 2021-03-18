from typing import *
from decimal import Decimal
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model

from rest_framework.test import APIRequestFactory, APIClient, APITestCase
from rest_framework import status

from django_basket.rest.serializers import BasketSerializer
from django_basket.models import BaseBasket
from django_basket.contrib.basket import BasketAggregator
from django_basket.shortcuts import get_basket_items_amount

from example_apps.products.models import Product, BasketItem
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
        aggregator = BasketAggregator(basket)
        aggregator.create_items([
            {"product": self.product1, "amount": 1},
            {"product": self.product2, "amount": 3},
            {"product": self.product3, "amount": 5},
        ])
        response = self.client.get("/api/basket/receive/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        basket = BaseBasket.objects.first()
        self.assertEqual(response.data, BasketSerializer(basket).data)

    def test_create(self):
        response = self.client.post(
            "/api/basket/create/items/",
            data={"basket_items": [
                {"product": self.product1.id, "amount": 1},
                {"product": self.product2.id, "amount": 3},
                {"product": self.product3.id, "amount": 5},
            ]},
            format="json"
        )
        basket = BaseBasket.objects.first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, BasketSerializer(basket).data)
        self.assertEqual(basket.price, self.product1.price + self.product2.price * 3 + self.product3.price * 5)
        self.assertEqual(get_basket_items_amount(basket), 9)

    def test_adding(self):
        basket_item1 = BasketItem.objects.create(product=self.product1, amount=1, price=self.product1.price)
        basket_item2 = BasketItem.objects.create(product=self.product2, amount=2, price=self.product2.price * 2)
        response = self.client.post(
            "/api/basket/add/",
            data={"basket_items": [basket_item1.id, basket_item2.id]},
            format="json"
        )
        basket = BaseBasket.objects.first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, BasketSerializer(basket).data)
        self.assertEqual(basket.price, self.product1.price + self.product2.price * 2)
        self.assertEqual(get_basket_items_amount(basket), 3)

    def test_remove(self):
        self.test_create()
        basket = BaseBasket.objects.first()
        basket_item = basket.basket_items.first()
        expected_amount_after_removing = get_basket_items_amount(basket) - basket_item.amount
        response = self.client.post("/api/basket/remove/", data={"basket_items": basket_item.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(get_basket_items_amount(basket), expected_amount_after_removing)

    def test_clear(self):
        self.test_create()
        response = self.client.post("/api/basket/clean/")
        basket = BaseBasket.objects.first()
        self.assertEqual(get_basket_items_amount(basket), 0)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(basket.price, 0)

    def test_amount_getter(self):
        response = self.client.post(
            "/api/basket/create/items/",
            data={"basket_items": [
                {"product": self.product1.id, "amount": 1},
                {"product": self.product2.id, "amount": 3},
                {"product": self.product3.id, "amount": 5},
            ]},
            format="json"
        )
        basket = BaseBasket.objects.first()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, BasketSerializer(basket).data)
        self.assertEqual(basket.price, self.product1.price + self.product2.price * 3 + self.product3.price * 5)
        amount_response = self.client.get("/api/basket/amount/")
        self.assertEqual(amount_response.status_code, status.HTTP_200_OK)
        self.assertEqual(amount_response.data, {"amount": 9})
