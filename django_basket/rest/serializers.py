from typing import Optional, Union, List, Type

from rest_framework import serializers

from django_basket.models import get_basket_model, BaseBasket
from django_basket.models.item import DynamicBasketItem
from ..settings import basket_settings
from ..utils import load_module


def get_basket_item_serializer_class() -> Optional[Type[serializers.Serializer]]:
    serializer_class = load_module(basket_settings.items_serializer)
    if serializer_class:
        return serializer_class
    return None


BasketRemovingModel = (
    DynamicBasketItem
    if basket_settings.is_dynamic
    else load_module(basket_settings.basket_item_model)
)
BasketItemsSerializer = get_basket_item_serializer_class()
BasketItemCreateSerializer = load_module(basket_settings.basket_item_create_serializer, BasketItemsSerializer)


def _get_basket_create_serializer_class():
    if BasketItemCreateSerializer:
        class KlassSerializer(serializers.Serializer):
            basket_items = serializers.ListSerializer(
                child=BasketItemCreateSerializer(), allow_empty=False
            )
    else:
        class KlassSerializer(serializers.Serializer):
            basket_items = serializers.PrimaryKeyRelatedField(
                queryset=load_module(basket_settings.basket_item_model).objects.all(),
                many=True,
            )
    return KlassSerializer


BasketItemsCreateSerializer = _get_basket_create_serializer_class()


class DynamicProductSerializer(serializers.ModelSerializer):
    item = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DynamicBasketItem
        fields = ("id", "item")

    @staticmethod
    def get_item(obj: DynamicBasketItem) -> Union[serializers.Serializer, List[Union[int, str]]]:
        if BasketItemsSerializer:
            return BasketItemsSerializer(obj.content_object).data
        return obj.content_object.pk


class BasketSerializer(serializers.ModelSerializer):
    basket_items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = get_basket_model()
        fields = "__all__"

    @staticmethod
    def get_basket_items(obj: Type[BaseBasket]) -> Union[serializers.Serializer, List[Union[int, str]]]:
        basket_items = obj.basket_items.all()
        if basket_settings.is_dynamic:
            return DynamicProductSerializer(basket_items, many=True).data
        if BasketItemsSerializer:
            return BasketItemsSerializer(basket_items, many=True).data
        return list(basket_items.values_list("pk", flat=True))


class BasketAddSerializer(serializers.Serializer):
    basket_items = serializers.PrimaryKeyRelatedField(
        queryset=load_module(basket_settings.basket_item_model).objects.all(),
        many=True,
    )


class BasketRemoveSerializer(serializers.Serializer):
    basket_items = serializers.PrimaryKeyRelatedField(
        queryset=BasketRemovingModel.objects.all(),
        many=True,
    )
