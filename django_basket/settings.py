from typing import Any, Optional

from django.conf import settings
from django.db import connection


SETTINGS_BLOCK = "DJANGO_BASKET"


class Settings:

    def __init__(self):
        self._settings = {}
        self.default_settings = getattr(settings, SETTINGS_BLOCK, {})

    def add(self, name, config=None, default=None):
        self._settings[name] = self.default_settings.get(config, default) if config else default

    def __getattribute__(self, name):
        local_settings = super().__getattribute__("_settings")
        if name in local_settings:
            return local_settings.get(name)
        return super().__getattribute__(name)


basket_settings = Settings()

# General
basket_settings.add("is_postgres", default=(connection.vendor == "postgresql"))
basket_settings.add("is_dynamic", "is_dynamic_basket_item_field", False)
basket_settings.add("is_delete_removing", "is_delete_removing", False)
basket_settings.add("adding_function", "basket_item_adding")
basket_settings.add("empty_function", "empty_basket")
basket_settings.add("create_empty_basket_function", "create_empty_basket")
basket_settings.add("basket_item_aggregator", "item_aggregator")
basket_settings.add("remove_functions", "remove_items")
basket_settings.add("is_update_while_merging", "is_update_while_merging", False)
basket_settings.add("merging", "merging")
basket_settings.add("items_create_function", "items_create")
basket_settings.add("basket_items_amount", "basket_amount_calculation")
basket_settings.add("is_merging_on_login", "is_merging_on_login", True)
# Price stuff
basket_settings.add("price_field_name", "price_field_name", "price")
basket_settings.add("price_calc_function", "price_calculating")
# Basket model
basket_settings.add("basket_item_model", "item_model")
basket_settings.add("basket_model", "basket_model")
# Serializers
basket_settings.add("basket_serializer", "basket_serializer")
basket_settings.add("items_serializer", "items_serializer")
basket_settings.add("basket_adding_serializer", "adding_serializer")
basket_settings.add("basket_item_create_serializer", "item_create_serializer")
basket_settings.add("basket_items_create_serializer", "items_create_serializer")
# Views
basket_settings.add("retrieve_view", "retrieve_view")
basket_settings.add("adding_view", "adding_view")
basket_settings.add("removing_view", "removing_view")
basket_settings.add("clean_view", "clean_view")
basket_settings.add("add_items_view", "add_items_view")
basket_settings.add("items_amount_view", "items_amount_view")
# Admin
basket_settings.add("basket_admin", "basket_admin")
basket_settings.add("basket_item_admin_inline", "basket_item_admin_inline")
