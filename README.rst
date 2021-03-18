DJANGO-IB-BASKET |PiPI version|
================

|Coverage| |Build Status|

Implement basket fullstack basket functionality.

Simple usage
------------

Create you basket item model:

.. code:: python

   # product/models.py

   from django.db import models


   class Product(models.Model):
       title = models.CharField(max_length=255)
       price = models.FloatField()


   class BasketItem(models.Model):
       amount = models.IntegerField()
       price = models.FloatField()
       product = models.ForeignKey(
           Product,
           on_delete=models.CASCADE,
           related_name="basket_items",
       )

Than config it in basket settings

.. code:: python

   # app/settings.py
   ...
   DJANGO_BASKET = {
       "item_model": "product.models.BasketItem",
   }
   ...

Add basket routers

.. code:: python

   # app/urls.py
   from django.urls import path, include
   ...
   urlpatterns = [
       ...,
       path('api/', include("django_basket.rest.urls")),
   ]
   ...

Now you can use simple basket EPs.

``api/basket/`` - Receive basket. Use GET request method, will return
structure like:

.. code:: json

   {
       "id": 26,
       "basket_items": [1],
       "created_at": "2020-11-17T15:03:22.840461Z",
       "updated_at": "2020-11-17T15:03:36.129638Z",
       "price": "2.00",
       "session_id": "k7dcwn9a01m3x31b789xd3xpsxqueaso",
       "user": null
   }

To customize basket item receiving structure, create basket item
serializer:

.. code:: python

   # product/basket.py
   from rest_framework import serializers
   from product.models import BasketItem

   class BasketItemSerializer(serializers.ModelSerializer):

       class Meta:
           model = BasketItem
           fields = "__all__"

And config settings:

.. code:: python

   # app/settings.py
   ...
   DJANGO_BASKET = {
       "item_model": "product.models.BasketItem",
       "items_serializer": "product.basket.BasketItemSerializer",
   }
   ...

Now ``api/basket/`` EP will return advance structure like:

.. code:: json

   {
       "id": 26,
       "basket_items": [
           {
               "id": 1,
               "amount": 2,
               "price": 2.0,
               "product": 1
           }
       ],
       "created_at": "2020-11-17T15:03:22.840461Z",
       "updated_at": "2020-11-17T15:03:36.129638Z",
       "price": "2.00",
       "session_id": "k7dcwn9a01m3x31b789xd3xpsxqueaso",
       "user": null
   }

``api/basket/remove/`` - Removes items from basket. Use POST method,
apply structure like:

.. code:: json

   {
       "basket_items": [1]
   }

And return same as basket receive structure.

``api/basket/create/items/`` - Custom basket items adding. To customize
adding process, create item adding serializer and basket creation
creator:

.. code:: python

   # product/basket.py
   from typing import List, Dict
   from rest_framework import serializers
   from product.models import BasketItem
   ...
   class BasketItemCreateSerializer(serializers.ModelSerializer):

       class Meta:
           model = BasketItem
           fields = ("product", "amount")


   def create_item(basket: "BaseBasket", validated_data: List[Dict]) -> List[BasketItem]:
       # {"basket_items": [{"product": 1, "amount":2}]}
       adding_items = list()
       for item in validated_data:
           item["price"] = item.get("product").price * item.get("amount")
           adding_items.append(BasketItem.objects.create(**item))
       return adding_items

That config it in settings file:

.. code:: python

   # app/settings.py

   DJANGO_BASKET = {
       "item_model": "product.models.BasketItem",
       "items_serializer": "product.basket.BasketItemSerializer",
       "item_create_serializer": "product.basket.BasketItemCreateSerializer",
       "items_create": "product.basket.create_item",
   }

Now you can use advance basket items adding. Set POST method request to
``api/basket/create/items/`` with body:

.. code:: json

   {
       "basket_items": [
           {"product": 1, "amount": 2},
           {"product": 2, "amount": 1}
       ]
   }

Settings
--------

All basket configuration contain in ``DJANGO_BASKET`` block.

``is_dynamic_basket_item_field`` - Boolean type. Enable a dynamic basket
item models. Basket item will contain generic relation to any table
which implement item stuff.

``basket_item_adding`` - Path to custom adding to function
(``Callable[[BasketHelper, List], List]``). If need to customize adding
to basket calculation, use this setting.

``empty_basket`` - Path to custom empty to function
(``Callable[[BasketHelper, List], List]``).

.. code:: python

   from django_basket.contrib.basket import BasketAggregator


   def empty_basket(helper: BasketAggregator):
       ...

``create_empty_basket`` - Path to custom implementation of empty basket
creation.

.. code:: python

   from django.contrib.auth import get_user_model
   from django_basket.models import get_basket_model

   User = get_user_model()
   BasketModel = get_basket_model()

   def get_empty_basket(user: User=None, **kwargs) -> BasketModel:
       ...

``item_aggregator`` - Path to location custom basket item helper. Must
be nested from ``django_basket.contrib.item.BasketItem``.

``remove_items`` - Path to custom remove items function.

.. code:: python

   from typing import List
   from django_basket.contrib.basket import BasketAggregator


   def remove(helper: BasketAggregator, items: List[Model]):
       ...

``is_update_while_merging`` - Boolean, config is update basket task
while basket merging. Default ``False``

``merging`` - Path to custom merging function.

.. code:: python

   from django_basket.models import get_basket_model

   BasketModel = get_basket_model()

   def _merge(basket: BasketModel, proxy: BasketModel):
       ...

``items_create`` - Path to function which create basket items. Will get
validated data param which is the array of ``item_create_serializer``
structure.

.. code:: python

   from typing import List, Dict
   from django_basket.models import get_basket_model
   from product.models import BasketItem

   BasketModel = get_basket_model()

   def items_create(basket: BasketModel, validated_data: List[Dict]) -> List[BasketItem]:
       ...

``get_basket_items_amount`` - Path to function which get basket items
amount.

.. code:: python

   from django_basket.contrib.basket import BasketAggregator


   def get_basket_items_amount(helper: BasketAggregator):
       ...

``is_merging_on_login`` - Boolean, is merge old basket with
authenticated user basket on login.

``price_field_name`` - String, name of basket item price field. Default
value - ``price``.

``price_calculating`` - Path to basket total price calculating function.

.. code:: python

   from django_basket.contrib.basket import BasketAggregator


   def calculation_price(helper: BasketAggregator):
       ...

``item_model`` - Path to custom basket item model. Must contain price
fields, with the same name as ``price_field_name``

``basket_model`` - Path to custom basket. Nested from
``django_basket.models.BaseBasket``.

``basket_serializer`` - Path to basket receive serializer class.

``items_serializer`` - Path to basket item serializer.

``adding_serializer`` - Path to basket adding serializer. Used in
``api/basket/add/``.

``item_create_serializer`` - Path to nested basket items creation
serializer. Used in ``api/basket/create/items/``.

``items_create_serializer`` - Path to general basket items creations
serializer, which contain ``item_create_serializer`` and used in
``api/basket/create/items/``.

``retrieve_view`` - Path to custom retrieve basket view, used in
``api/basket/``.

``adding_view`` - Path to custom adding in basket view, used in
``api/basket/add/``.

``removing_view`` - Path to custom removing from basket view, used in
``api/basket/remove/``.

``clean_view`` - Path to custom basket cleaning view, used in
``api/basket/clean/``.

``add_items_view`` - Path to custom basket items creation, used in
``api/basket/create/items/``.

``items_amount_view`` - Path to custom basket amount of items receive,
used in ``api/basket/amount/``.

``basket_admin`` - Path to custom basket admin class.

``basket_item_admin_inline`` - Path to custom basket item admin inline
class.
