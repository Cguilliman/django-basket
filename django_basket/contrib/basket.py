from typing import *
from decimal import Decimal

from django.db.models import Model
from django.contrib.auth import get_user_model

from django_basket.utils import settings_function
from ..settings import basket_settings
from ..models.item import DynamicBasketItem
from .base import BasketHelper as DefaultBasketHelper
from .item import basket_use_case_class


User = get_user_model()


class BasketAggregator(DefaultBasketHelper):

    def __init__(self, basket):
        super().__init__(basket)
        self.items_aggregator = basket_use_case_class(basket)

    @settings_function(func_path=basket_settings.adding_function)
    def add_items(self, products: List[Model]) -> List[Model]:
        """
            Implement adding item to basket,
            delegate adding process to basket item helper
            than recalculate total basket price
        """
        adding_items = self.items_aggregator.items_adding(products)
        self.calculate_price()
        return adding_items

    def add(self, item: Model) -> Model:
        """Add single basket item"""
        return self.add_items([item])[0]

    def add_many(self, items: List[Model]) -> List[Model]:
        """Add multiple basket item"""
        return self.add_items(items)

    def create_items(self, data: List[Dict]):
        """Create basket items and add it to available basket"""
        items, is_custom_function = self.items_aggregator.items_create(data)
        try:
            return self.add_many(items)
        except Exception as e:
            if is_custom_function:
                raise AttributeError(
                    "Basket item creation is not implemented, fill in `items_create_function` setting"
                )
            raise e

    @settings_function(func_path=basket_settings.price_calc_function)
    def calculate_price(self):
        """Calculate and save total basket price"""
        self.basket.price = Decimal(
            self.items_aggregator.items_total_price()
        )
        self.basket.save()

    @settings_function(func_path=basket_settings.empty_function)
    def empty_basket(self):
        """Delete all items from basket"""
        if basket_settings.is_dynamic:
            # Delete dynamic products
            self.basket.basket_items.all().delete()
        else:
            # Will delete all related objects if enable delete while removing
            # Else clear basket items relations
            if basket_settings.is_delete_removing:
                self.basket.basket_items.all().delete()
            else:
                self.basket.basket_items.clear()
        self.calculate_price()

    @settings_function(func_path=basket_settings.remove_functions)
    def remove(self, items: List[Model]):
        """Remove items from basket"""
        if basket_settings.is_dynamic:
            (
                DynamicBasketItem.objects
                .filter(
                    id__in=[item.id for item in items],
                    basket=self.basket
                )
                .delete()
            )
        else:
            self.basket.basket_items.remove(*items)
            if basket_settings.is_delete_removing:
                list(map(lambda item: item.delete(), items))

        self.calculate_price()
