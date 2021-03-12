from typing import Union, Iterable, List
from decimal import Decimal

from django.db.models import Model
from django_basket.models import BaseBasket


class BasketHelper:
    basket = None

    def __init__(self, basket: BaseBasket):
        self.basket = basket


class BaseBasketItemHelper(BasketHelper):

    def items_adding(self, items: Iterable[Model]) -> Iterable[Model]:
        raise NotImplemented

    def items_total_price(self) -> Union[int, float, Decimal]:
        raise NotImplemented

    def items_create(self, validated_data: List) -> Iterable[Model]:
        raise NotImplemented
