from typing import Iterable, Optional

from django.db.transaction import atomic
from django_basket.contrib.basket import BasketAggregator
from django_basket.utils import settings_function
from django_basket.models import BaseBasket as BasketModel
from django_basket.settings import basket_settings


__all__ = ("merge", "merge_baskets_queryset")


@settings_function(func_path=basket_settings.merging)
def _merge(basket, proxy):
    helper = BasketAggregator(basket)
    # Add new objects from proxy basket
    helper.add_many(list(proxy.basket_items.all()))
    # Recalculate basket total price
    helper.calculate_price()
    proxy.delete()


def merge(basket: BasketModel, proxy: BasketModel, **kwargs):
    """
        Merge two baskets in one.

        Args:
            basket: BasketModel - core basket
            proxy: BasketModel - proxy basket, all contained items will merged in core basket
            kwargs: - additional basket fields which will added after merging
        Return:
            basket: BasketModel - result basket object
    """
    with atomic():
        _merge(basket, proxy)
        # Save extra data in basket
        for key, value in kwargs.items():
            setattr(basket, key, value)
        basket.save()
    return basket


def merge_baskets_queryset(baskets: Iterable, general: Optional[BasketModel] = None):
    """
        Merge iterable collection of baskets.

        Args:
            baskets: Iterable[BasketModel] - Collection of baskets
            general: Optional[BasketModel] - General basket, all baskets will merged with this one
        Return:
            general: BasketModel - general basket
    """
    iterated = iter(baskets)
    if general is None:
        general = next(iterated)

    for proxy_basket in iterated:
        merge(general, proxy_basket)
    return general
