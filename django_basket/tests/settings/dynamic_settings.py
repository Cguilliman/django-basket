from .settings import *

DJANGO_BASKET = {
    # # Dynamic basket items settings
    "is_dynamic_basket_item_field": True,
    "item_model": "example_apps.products.models.BasketItem",
    "items_serializer": "example_apps.products.basket.BasketItemSerializer",
    "item_create_serializer": "example_apps.products.basket.BasketItemCreateSerializer",
    "items_create": "example_apps.products.basket.create_items",
    "item_helper": "example_apps.products.basket.DynamicBasketItemHelper",
}
