from typing import Union, Iterable, Type, List, Tuple
from decimal import Decimal

from django.db.models import Sum, Model
from django.db.models.functions import Coalesce

from django_basket.utils import load_module
from ..settings import basket_settings
from ..models.item import DynamicBasketItem as DynamicBasketItemModel
from .base import BaseBasketItemHelper


class BasketItemAggregator(BaseBasketItemHelper):

    def items_adding(self, items: List[Model]) -> List[Model]:
        """Add products to basket"""
        self.basket.basket_items.add(*items)
        return items

    def items_total_price(self) -> Union[int, float, Decimal]:
        """Calculate sum of products prices"""
        res = self.basket.basket_items.all().aggregate(
            total_price=Coalesce(Sum(basket_settings.price_field_name), 0)
        ).get("total_price")
        return res

    def items_create(self, validated_data: List) -> Tuple[List[Model], bool]:
        """Create basket items, use only custom implementation"""
        creation_function = load_module(basket_settings.items_create_function)
        if not creation_function or not callable(creation_function):
            return validated_data, False

        return creation_function(self.basket, validated_data), True


class DynamicBasketItemAggregator(BasketItemAggregator):

    def items_adding(self, items: Iterable[Model]) -> Iterable[Model]:
        """Add products to basket"""
        products = DynamicBasketItemModel.create_item(items)
        return super().items_adding(products)

    def items_total_price(self) -> Union[int, float, Decimal]:
        """Calculate sum of products prices"""
        return sum([
            getattr(item, basket_settings.price_field_name)
            for item in self.basket.basket_items.all()
        ])


basket_use_case_class = load_module(
    basket_settings.basket_item_aggregator,
    default=DynamicBasketItemAggregator if basket_settings.is_dynamic else BasketItemAggregator,
)
