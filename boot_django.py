# boot_django.py
#
# This file sets up and configures Django. It's used by scripts that need to
# execute as if running in a Django server.
import os
import django
from django.conf import settings
# from django_basket.tests import settings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "django_basket"))


def boot_django():
    settings.configure(
        DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },

        CACHES = {
            'default': {
                # This cache backend is OK to use in development and testing
                # but has the potential to break production setups with more than on process
                # due to each process having their own local memory based cache
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            }
        },

        SITE_ID = 1,

        MIDDLEWARE = [
            'django.middleware.common.CommonMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],

        AUTHENTICATION_BACKENDS = [
            'django.contrib.auth.backends.ModelBackend',
        ],

        PASSWORD_HASHERS = [
            'django.contrib.auth.hashers.MD5PasswordHasher',
        ],

        # ROOT_URLCONF = 'example_apps.urls'

        INSTALLED_APPS = [
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.sites',
            'django.contrib.messages',
            'django.contrib.admin',

            'example_apps.products',
            'django_basket',
        ],

        TEMPLATES = [
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ],

        SECRET_KEY = 'too-secret-for-test',

        USE_I18N = False,

        USE_L10N = False,

        USE_TZ = False,

        LOGIN_REDIRECT_URL = '/admin/',

        DJANGO_BASKET = {
            # # Dynamic basket items settings
            # "is_dynamic_basket_item_field": True,
            # "item_model": "product.models.BasketItem",
            # "items_serializer": "product.basket.BasketItemSerializer",
            # "item_create_serializer": "product.basket.BasketItemCreateSerializer",
            # "items_create_function": "product.basket.create_item",
            # # "is_delete_removing": True,
            # # "basket_amount_calculation": "product.basket.get_basket_items_amount",
            # "item_helper": "product.basket.DynamicBasketItemHelper",

            "is_dynamic_basket_item_field": True,
            "item_model": "example_apps.products.models.BasketItem",
            "items_serializer": "example_apps.products.basket.BasketItemSerializer",
            "item_create_serializer": "example_apps.products.basket.BasketItemCreateSerializer",
            "items_create_function": "example_apps.products.basket.create_item",
            "is_delete_removing": True,
            "basket_amount_calculation": "example_apps.products.basket.get_basket_items_amount",
            "item_helper": "example_apps.products.basket.BasketItemHelper",

            # "is_merging_on_login": False,
        },
    )
    django.setup()


from django.core.management import call_command

boot_django()
call_command("makemigrations")
