from typing import Union, List, Type
from decimal import Decimal

from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from ..settings import basket_settings
from ..utils import load_module


# TODO: Re-factor basket-basketItem relation to foreignKey from item
#       Create base basket item model with implemented relation
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
        return getattr(self.content_object, basket_settings.price_field_name, Decimal(0))


# TODO: Make availability to set custom dynamic basket item model
def get_basket_item_model() -> Type[Union[DynamicBasketItem, models.Model]]:
    if basket_settings.is_dynamic:
        return DynamicBasketItem
    product_model = load_module(basket_settings.basket_item_model)
    if not product_model:
        raise ImproperlyConfigured("`basket_item_model` is empty")
    return product_model
