from .models import BaseBasket
from .contrib.basket import BasketAggregator
from .contrib.selectors import get_session_basket
from .utils import settings_function
from .settings import basket_settings


__all__ = (
    "get_basket_aggregator",
    "get_basket_from_request",
    "get_basket_items_amount",
)


def get_basket_from_request(request) -> BaseBasket:
    """Get basket from request"""
    if not request.session.exists(request.session.session_key):
        request.session.create()
    user = request.user if request.user.is_authenticated else None
    return get_session_basket(request.session, user)


def get_basket_aggregator(request) -> BasketAggregator:
    """Get basket helper by request"""
    return BasketAggregator(get_basket_from_request(request))


@settings_function(func_path=basket_settings.basket_items_amount)
def get_basket_items_amount(basket: BaseBasket) -> int:
    return basket.basket_items.count()
