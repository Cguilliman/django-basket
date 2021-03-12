from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoBasketConfig(AppConfig):
    name = 'django_basket'
    verbose_name = _('Basket')
