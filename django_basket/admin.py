from django.contrib import admin

from .settings import basket_settings
from .models.basket import get_basket_model
from .models.item import DynamicBasketItem
from .utils import load_module


Basket = get_basket_model()


if basket_settings.is_dynamic:
    admin.site.register(DynamicBasketItem)


class BasketItemInline(admin.StackedInline):
    model = Basket.basket_items.through
    extra = 0


basket_item_inline = load_module(basket_settings.basket_item_admin_inline, default=BasketItemInline)


class BasketAdmin(admin.ModelAdmin):
    list_display = (
        "id", "user", "price", "created_at", "updated_at"
    )
    readonly_fields = (
        "id", "created_at", "updated_at", "session_id"
    )
    exclude = ("basket_items", )
    inlines = (basket_item_inline, )


admin.site.register(Basket, load_module(basket_settings.basket_admin, default=BasketAdmin))
