from typing import Union, List, Type
from decimal import Decimal

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from ..settings import basket_settings
from ..utils import load_module


class DynamicBasketItem(models.Model):
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        abstract = (False if basket_settings.is_dynamic else True)
        verbose_name = _("Dynamic product")
        verbose_name_plural = _("Dynamic products")

    @property
    def price(self) -> Union[int, float, Decimal]:
        return getattr(
            self.content_object,
            basket_settings.price_field_name  # `price` by default
        )

    # TODO: Re-factor
    @classmethod
    def create_item(cls, objs) -> List["DynamicBasketItem"]:
        """Create products and return in collection"""
        if basket_settings.is_postgres:
            # postgres db backend after bulk creation
            # return objects with auto incremented primary field
            return cls.objects.bulk_create([
                cls(
                    content_type=ContentType.objects.get_for_model(obj),
                    object_id=obj.id,
                ) for obj in objs
            ])

        products = []
        for obj in objs:
            product = cls(
                content_type=ContentType.objects.get_for_model(obj),
                object_id=obj.id,
            )
            product.save()
            products.append(product)

        return products


def get_basket_item_model() -> Type[Union[DynamicBasketItem, models.Model]]:
    if basket_settings.is_dynamic:
        return DynamicBasketItem
    product_model = load_module(basket_settings.basket_item_model)
    if not product_model:
        raise ImproperlyConfigured("`basket_item_model` is empty")
    return product_model
