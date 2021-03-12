from typing import *
from operator import or_
from functools import reduce

from django.db.models import Q
from django.contrib.auth import get_user_model

from .merging import merge, merge_baskets_queryset
from django_basket.settings import basket_settings
from django_basket.models.basket import BaseBasket as BasketModel
from django_basket.utils import settings_function


__all__ = ("get_empty_basket", "get_session_basket")


User = get_user_model()


@settings_function(func_path=basket_settings.create_empty_basket_function)
def get_empty_basket(user: User = None, **kwargs) -> BasketModel:
    return BasketModel.objects.create(
        user=user,
        price=0,
        **kwargs
    )


def get_basket(**kwargs) -> Optional[BasketModel]:
    # Generate filters to search baskets
    filters = reduce(or_, [
        Q(**{key: value})
        for key, value in kwargs.items()
    ])
    qs = BasketModel.objects.filter(filters)
    # If more than one basket - merge
    if qs.count() > 1:
        return merge_baskets_queryset(qs)
    basket = qs.first()
    return basket


def get_session_keys_basket(
    current_session_key: str,
    old_session_key: str = None,
    user: User = None,
) -> [BasketModel, bool]:
    """
        Get actual basket by sessions keys.

        Args:
             current_session_key: str - Actual session key
             old_session_key: Optional[str] - Old session key, not required
             user: Optional[User] - Current authenticated user, be careful with anonymous user
        Return:
            current basket: Basket - current basket
            is merged: bool - marker, is current basket merged with another, old session basket
    """
    if user and not user.is_authenticated:
        user = None
    old_basket: Optional[BasketModel] = get_basket(session_id=old_session_key) if old_session_key else None
    current_basket: Optional[BasketModel] = get_basket(session_id=current_session_key, user=user)
    if not current_basket:
        current_basket: BasketModel = get_empty_basket(
            session_id=current_session_key, user=user
        )
    if old_basket and basket_settings.is_merging_on_login:
        return merge(current_basket, old_basket), True
    return current_basket, False


def get_session_basket(session, user: Optional[User] = None):
    """
        Get basket by session and authenticated user.

        Args:
            session: SessionStore - session store class.
            user: User - current authenticated user
    """
    basket, is_merged = get_session_keys_basket(
        session.session_key, session.get_marker(), user
    )
    if is_merged:
        session.delete_marker()
    return basket
