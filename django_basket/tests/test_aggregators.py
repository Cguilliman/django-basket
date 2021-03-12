from django.test import TestCase
from django.test.client import RequestFactory

from django_basket.shortcuts import get_basket_aggregator


class BasketAggregationTestCase(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_aggregator_getting(self):
        request = self.factory.get("/")
        print(get_basket_aggregator(request))
