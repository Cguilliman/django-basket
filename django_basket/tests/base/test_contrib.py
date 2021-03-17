from django.test import TestCase
from django.test.client import RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ImproperlyConfigured

from django_basket.shortcuts import (
    get_basket_aggregator,
    get_basket_items_amount,
)
from django_basket.contrib.basket import BasketAggregator
from django_basket.contrib.selectors import get_empty_basket, get_basket, get_session_basket
from django_basket.contrib.merging import merge_baskets_queryset, merge
from django_basket.models import BaseBasket, get_basket_item_model

from example_apps.products.models import Product
from ..utils import overwrite_settings


User = get_user_model()


class MergingSelectorsTestCase(TestCase):

    def setUp(self):
        self.username = "user"
        self.email = "user@mail.com"
        self.password = "password"
        self.user = User.objects.create_user(self.username, self.email, self.password)
        # Mock request
        self.request = RequestFactory().get("/admin/login/")
        self.request.session = self.client.session
        self.request.user = AnonymousUser()
        # Products
        self.product1 = Product.objects.create(title="title1", price=1)
        self.product2 = Product.objects.create(title="title2", price=2)
        self.product3 = Product.objects.create(title="title3", price=3)

    def test_merge_basket_queryset(self):
        self.assertFalse(BaseBasket.objects.exists())
        basket1 = BasketAggregator(get_empty_basket())
        basket2 = BasketAggregator(get_empty_basket())
        basket3 = BasketAggregator(get_empty_basket())
        basket4 = BasketAggregator(get_empty_basket())
        self.assertEqual(BaseBasket.objects.count(), 4)
        basket1.create_items([
            {"product": self.product1, "amount": 1},
        ])
        basket2.create_items([
            {"product": self.product2, "amount": 2},
        ])
        basket3.create_items([
            {"product": self.product3, "amount": 2},
        ])
        basket4.create_items([
            {"product": self.product3, "amount": 2},
        ])
        merge_baskets_queryset([basket1.basket, basket2.basket], basket3.basket)
        general_basket = merge_baskets_queryset(BaseBasket.objects.all())
        self.assertEqual(BaseBasket.objects.count(), 1)
        self.assertEqual(get_basket_items_amount(general_basket), 7)
        self.assertEqual(general_basket.price, (
            self.product1.price
            + self.product2.price * 2
            + self.product3.price * 4
        ))

    def test_merge_with_extra_data(self):
        basket1 = BasketAggregator(get_empty_basket())
        basket2 = BasketAggregator(get_empty_basket())
        basket1.create_items([
            {"product": self.product1, "amount": 1},
        ])
        basket2.create_items([
            {"product": self.product2, "amount": 2},
        ])
        general_basket = merge(basket1.basket, basket2.basket, price=200)
        self.assertEqual(general_basket.price, 200)

    def test_session_merging(self):
        anonymous_aggregator = get_basket_aggregator(self.request)
        anonymous_aggregator.create_items([
            {"product": self.product1, "amount": 1},
        ])
        self.request.user = self.user
        self.request.session.cycle_key()
        user_aggregator = get_basket_aggregator(self.request)
        user_aggregator.create_items([
            {"product": self.product1, "amount": 1},
            {"product": self.product2, "amount": 2},
        ])
        self.assertEqual(BaseBasket.objects.count(), 1)
        self.assertEqual(get_basket_items_amount(user_aggregator.basket), 4)
        self.assertEqual(user_aggregator.basket.price, self.product1.price * 2 + self.product2.price * 2)

    def test_get_basket(self):
        basket1 = BasketAggregator(get_empty_basket(self.user))
        basket2 = BasketAggregator(get_empty_basket(self.user))
        basket1.create_items([
            {"product": self.product1, "amount": 1},
            {"product": self.product2, "amount": 2},
        ])
        basket2.create_items([
            {"product": self.product1, "amount": 1},
        ])
        basket = get_basket(user=self.user)
        self.assertEqual(get_basket_items_amount(basket), 4)
        self.assertEqual(basket.price, self.product1.price * 2 + self.product2.price * 2)

    def test_get_basket_by_session_keys(self):
        get_session_basket(self.request.session, AnonymousUser())
        self.assertEqual(BaseBasket.objects.count(), 1)

    def test_not_exists_basket_item_model(self):
        with overwrite_settings(basket_item_model=None):
            with self.assertRaises(ImproperlyConfigured):
                get_basket_item_model()
