from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from ..contrib.basket import BasketAggregator
from ..settings import basket_settings
from ..models import get_basket_model
from .serializers import (
    BasketSerializer,
    BasketAddSerializer,
    BasketRemoveSerializer,
    BasketItemsCreateSerializer
)
from ..utils import load_module
from ..shortcuts import get_basket_from_request, get_basket_aggregator, get_basket_items_amount

BasketSerializer = load_module(basket_settings.basket_serializer, BasketSerializer)
BasketAddSerializer = load_module(basket_settings.basket_adding_serializer, BasketAddSerializer)
BasketItemsCreateSerializer = load_module(basket_settings.basket_items_create_serializer, BasketItemsCreateSerializer)


class BasketGettingViewMixin:
    model = get_basket_model()

    def get_object(self):
        return get_basket_from_request(self.request)


class BasketRetrieveAPIView(BasketGettingViewMixin, RetrieveAPIView):
    serializer_class = BasketSerializer


class BasketItemCreateSerialize(BasketGettingViewMixin, CreateAPIView):
    serializer_class = BasketItemsCreateSerializer

    def create(self, request, *args, **kwargs):
        # Get available basket
        basket = self.get_object()
        # Validate basket items fields
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Delegate item creation
        BasketAggregator(basket).create_items(
            serializer.validated_data.get("basket_items", [])
        )
        return Response(BasketSerializer(basket).data, status=status.HTTP_201_CREATED)


class BasketAddAPIView(BasketGettingViewMixin, CreateAPIView):
    serializer_class = BasketAddSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        basket = self.get_object()
        BasketAggregator(basket).add_many(serializer.validated_data.get("basket_items", []))
        return Response(BasketSerializer(basket).data, status=status.HTTP_201_CREATED)

    def get_object(self):
        return get_basket_from_request(self.request)


class BasketRemoveProductsAPIView(BasketGettingViewMixin, CreateAPIView):
    serializer_class = BasketRemoveSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        basket = self.get_object()
        BasketAggregator(basket).remove(serializer.validated_data.get("basket_items"))
        return Response(BasketSerializer(basket).data, status=status.HTTP_201_CREATED)

    def get_object(self):
        return get_basket_from_request(self.request)


class BasketCleanAPIView(BasketGettingViewMixin, APIView):

    def post(self, request, *args, **kwargs):
        BasketAggregator(self.get_object()).empty_basket()
        return Response({"status": "OK"}, status=status.HTTP_201_CREATED)


class BasketAmountAPIVIew(BasketGettingViewMixin, APIView):

    def get(self, request, *args, **kwargs):
        return Response(
            {"amount": get_basket_items_amount(self.get_object())},
            status=status.HTTP_200_OK
        )
