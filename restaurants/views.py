from rest_framework import viewsets
from .models import Restaurant, MenuItem
from .serializers import RestaurantSerializer, MenuItemSerializer
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter

class RestaurantViewSet(viewsets.ModelViewSet):
    """Lijst van restaurants is voor iedereen leesbaar"""
    queryset = Restaurant.objects.filter(is_active=True)
    serializer_class = RestaurantSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    #filterset_fields = ['city'] # Gebruikers kunnen nu ?city=Cairo doen
    search_fields = ['name', 'description'] # Zoekbalk functionaliteit
    permission_classes = [AllowAny]

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
