from .settings import *

DJANGO_BASKET = {
    "item_model": "example_apps.products.models.BasketItem",
    "basket_amount_calculation": "example_apps.products.basket.get_basket_items_amount",
}
