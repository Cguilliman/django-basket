from typing import *
from decimal import Decimal
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model

from django_basket.settings import basket_settings
from django_basket.shortcuts import get_basket_aggregator, get_basket_items_amount
from django_basket.models import BaseBasket

from example_apps.products.models import Product
from example_apps.products.basket import create_items
from ..utils import overwrite_settings


User = get_user_model()


class BasketAggregationTestCase(TestCase):

    def setUp(self):
        self.username = "user"
        self.email = "user@mail.com"
        self.password = "password"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        # Mock request
        self.request = RequestFactory().get("/admin/login/")
        self.request.session = self.client.session
        self.request.user = self.user
        # Products
        self.product1 = Product.objects.create(title="title1", price=1)
        self.product2 = Product.objects.create(title="title2", price=2)
        self.product3 = Product.objects.create(title="title3", price=3)

    def test_aggregator_getting(self):
        self.assertEqual(BaseBasket.objects.count(), 0)
        get_basket_aggregator(self.request)
        self.assertEqual(BaseBasket.objects.count(), 1)
        created_basket = BaseBasket.objects.first()
        self.assertEqual(created_basket.user, self.user)
        self.assertEqual(created_basket.price, Decimal(0))

    def test_adding(self):
        self.assertEqual(BaseBasket.objects.count(), 0)
        aggregator = get_basket_aggregator(self.request)
        item1, item2, item3 = create_items(
            aggregator.basket,
            [
                {"product": self.product1, "amount": 1},
                {"product": self.product2, "amount": 3},
                {"product": self.product3, "amount": 5},
            ]
        )
        aggregator.add(item1)
        self.assertEqual(aggregator.basket.price, Decimal(1))
        self.assertEqual(get_basket_items_amount(aggregator.basket), 1)
        aggregator.add(item2)
        self.assertEqual(aggregator.basket.price, Decimal(7))
        self.assertEqual(get_basket_items_amount(aggregator.basket), 4)
        aggregator.add(item3)
        self.assertEqual(aggregator.basket.price, Decimal(22))
        self.assertEqual(get_basket_items_amount(aggregator.basket), 9)

    def test_many_adding_and_empty(self):
        self.assertEqual(BaseBasket.objects.count(), 0)
        aggregator = get_basket_aggregator(self.request)
        aggregator.create_items([
            {"product": self.product1, "amount": 1},
            {"product": self.product2, "amount": 3},
            {"product": self.product3, "amount": 5},
        ])
        self.assertEqual(get_basket_items_amount(aggregator.basket), 9)
        self.assertEqual(aggregator.basket.price, Decimal(22))
        # Test basket empty
        aggregator.empty_basket()
        self.assertEqual(get_basket_items_amount(aggregator.basket), 0)
        self.assertEqual(aggregator.basket.price, Decimal(0))

    def test_removing(self):
        self.assertEqual(BaseBasket.objects.count(), 0)
        aggregator = get_basket_aggregator(self.request)
        item1, item2, item3 = aggregator.create_items([
            {"product": self.product1, "amount": 1},
            {"product": self.product2, "amount": 3},
            {"product": self.product3, "amount": 5},
        ])
        self.assertIn(item1, aggregator.basket.basket_items.all())
        aggregator.remove([item1])
        self.assertNotIn(item1, aggregator.basket.basket_items.all())
        self.assertIn(item2, aggregator.basket.basket_items.all())
        self.assertIn(item3, aggregator.basket.basket_items.all())
        aggregator.remove([item2, item3])
        self.assertEqual(get_basket_items_amount(aggregator.basket), 0)
        self.assertFalse(bool(item1.id))
        self.assertFalse(bool(item2.id))
        self.assertFalse(bool(item3.id))

    def test_removing_with_basket_delete(self):
        basket_settings._settings["is_delete_removing"] = False
        self.assertEqual(BaseBasket.objects.count(), 0)
        aggregator = get_basket_aggregator(self.request)
        items = aggregator.create_items([
            {"product": self.product1, "amount": 1},
            {"product": self.product2, "amount": 3},
            {"product": self.product3, "amount": 5},
        ])
        self.assertEqual(get_basket_items_amount(aggregator.basket), 9)
        aggregator.empty_basket()

        aggregator = get_basket_aggregator(self.request)
        items2 = aggregator.create_items([
            {"product": self.product1, "amount": 1},
            {"product": self.product2, "amount": 3},
            {"product": self.product3, "amount": 5},
        ])
        self.assertEqual(get_basket_items_amount(aggregator.basket), 9)
        aggregator.remove(items)

        for item in [*items, *items2]:
            self.assertTrue(bool(item))

    def test_not_implemented_items_creation(self):
        with overwrite_settings(items_create_function=None):
            basket_settings._settings["is_delete_removing"] = False
            self.assertEqual(BaseBasket.objects.count(), 0)
            aggregator = get_basket_aggregator(self.request)
            with self.assertRaises(TypeError):
                aggregator.create_items([
                    {"product": self.product1, "amount": 1},
                    {"product": self.product2, "amount": 3},
                    {"product": self.product3, "amount": 5},
                ])
