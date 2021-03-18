from django.urls import path, include

from . import views
from ..settings import basket_settings
from ..utils import load_module


urlpatterns = [
    path(
        "basket/",
        include(((
            path("receive/", load_module(basket_settings.retrieve_view, views.BasketRetrieveAPIView).as_view()),
            path("create/items/", load_module(basket_settings.add_items_view, views.BasketItemCreateSerialize).as_view()),
            path("add/", load_module(basket_settings.adding_view, views.BasketAddAPIView).as_view()),
            path("remove/", load_module(basket_settings.removing_view, views.BasketRemoveProductsAPIView).as_view()),
            path("clean/", load_module(basket_settings.clean_view, views.BasketCleanAPIView).as_view()),
            path("amount/", load_module(basket_settings.items_amount_view, views.BasketAmountAPIVIew).as_view()),
        ), "basket"))
    )
]
