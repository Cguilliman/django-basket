from typing import *
from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model

from django_basket.models.item import DynamicBasketItem
from django_basket.shortcuts import get_basket_aggregator, get_basket_items_amount
from django_basket.models import BaseBasket, get_basket_item_model

from example_apps.products.models import Product


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

    def test_adding(self):
        aggregator = get_basket_aggregator(self.request)
        _ = aggregator.add_many([self.product1, self.product2, self.product3])
        self.assertEqual(get_basket_items_amount(aggregator.basket), 3)

    def test_removing(self):
        self.assertEqual(BaseBasket.objects.count(), 0)
        aggregator = get_basket_aggregator(self.request)
        item1, item2, item3 = aggregator.create_items([
            {"product": self.product1, "amount": 1},
            {"product": self.product2, "amount": 3},
            {"product": self.product3, "amount": 5},
        ])
        self.assertIn(item1, aggregator.basket.basket_items.all())
        self.assertIn(item2, aggregator.basket.basket_items.all())
        self.assertIn(item3, aggregator.basket.basket_items.all())
        aggregator.remove([item1])
        self.assertNotIn(item1, aggregator.basket.basket_items.all())
        self.assertIn(item2, aggregator.basket.basket_items.all())
        self.assertIn(item3, aggregator.basket.basket_items.all())
        aggregator.remove([item2, item3])
        self.assertEqual(get_basket_items_amount(aggregator.basket), 0)
        self.assertFalse(DynamicBasketItem.objects.exists())

    def test_empty(self):
        self.assertEqual(BaseBasket.objects.count(), 0)
        aggregator = get_basket_aggregator(self.request)
        item1, item2, item3 = aggregator.create_items([
            {"product": self.product1, "amount": 1},
            {"product": self.product2, "amount": 3},
            {"product": self.product3, "amount": 5},
        ])
        self.assertIn(item1, aggregator.basket.basket_items.all())
        self.assertIn(item2, aggregator.basket.basket_items.all())
        self.assertIn(item3, aggregator.basket.basket_items.all())
        aggregator.empty_basket()
        self.assertNotIn(item1, aggregator.basket.basket_items.all())
        self.assertNotIn(item2, aggregator.basket.basket_items.all())
        self.assertNotIn(item3, aggregator.basket.basket_items.all())
        self.assertEqual(get_basket_items_amount(aggregator.basket), 0)
        self.assertFalse(DynamicBasketItem.objects.exists())
