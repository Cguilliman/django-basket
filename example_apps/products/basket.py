from typing import Dict, List

from django.db.models import Sum
from django.db.models.functions import Coalesce

from rest_framework import serializers
from django_basket.contrib.item import (
    BasketItemAggregator as DefaultBasketItemHelper,
    DynamicBasketItemAggregator as DefaultDynamicBasketItem,
    BaseBasketItemHelper
)

from .models import BasketItem


class BasketItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = BasketItem
        fields = "__all__"


class BasketItemCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = BasketItem
        fields = ("product", "amount")


class BasketItemHelper(DefaultBasketItemHelper):

    def items_adding(self, items: List):
        for item in items:
            if exist_item := self.basket.basket_items.filter(product=item.product).first():
                exist_item.amount += item.amount
                exist_item.price = exist_item.product.price * exist_item.amount
                exist_item.save()
                items.remove(item)
        return super().items_adding(items)


class DynamicBasketItemHelper(DefaultDynamicBasketItem):

    def items_adding(self, items: List):
        for item in items:
            exist_item = BasketItem.objects.filter(
                dynamic_basket_item__basket=self.basket,
                product=item.product
            ).first()
            if exist_item:
                exist_item.amount += item.amount
                exist_item.price = exist_item.product.price * exist_item.amount
                exist_item.save()
                items.remove(item)
        return super().items_adding(items)


def create_item(basket: "BaseBasket", validated_data: List[Dict]) -> List[BasketItem]:
    # {"basket_items": [{"product": 1, "amount":2}]}
    adding_items = list()
    for item in validated_data:
        item["price"] = item.get("product").price * item.get("amount")
        adding_items.append(BasketItem.objects.create(**item))
    return adding_items


def get_basket_items_amount(helper) -> int:
    return (
        helper
        .basket
        .basket_items
        .aggtetate(total_amount=Coalesce(Sum("amount"), 0))
        .get("total_amount")
    )
