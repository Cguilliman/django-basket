from django.db import models
# from django.contrib.contenttypes.fields import GenericRelation
# from django_basket.models import get_basket_item_model


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
    # dynamic_basket_item = GenericRelation(get_basket_item_model())
