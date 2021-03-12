from typing import Type
from decimal import Decimal

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from ..settings import basket_settings
from ..utils import load_module
from .item import get_basket_item_model


def get_basket_model() -> Type["BaseBasket"]:
    return load_module(
        path=basket_settings.basket_model,
        default=BaseBasket
    )


class BaseBasket(models.Model):
    created_at = models.DateTimeField(
        verbose_name=_("Created at"),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name=_("Updated at"),
        auto_now=True
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("User"),
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )
    basket_items = models.ManyToManyField(
        get_basket_item_model(),
        verbose_name=_("Basket item"),
        related_name="basket",
        blank=True
    )
    price = models.DecimalField(
        verbose_name=_('Price'),
        max_digits=10,
        decimal_places=2,
        default=Decimal(0)
    )
    session_id = models.CharField(
        verbose_name=_('Session id'),
        max_length=255,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = _("Basket")
        verbose_name_plural = _("Baskets")