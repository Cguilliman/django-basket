from contextlib import contextmanager
from copy import deepcopy

from django_basket.settings import basket_settings


@contextmanager
def overwrite_settings(**settings):
    default_settings = deepcopy(basket_settings._settings)
    try:
        basket_settings._settings.update(settings)
        yield
    finally:
        basket_settings._settings.update(default_settings)
