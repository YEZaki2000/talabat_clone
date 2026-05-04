from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        # Koppel de ingelogde gebruiker automatisch aan de bestelling
        serializer.save(customer=self.request.user)

    """
    def create(self, request, *args, **kwargs):
        \"""Aangepaste create om ook OrderItems in één keer te verwerken\"""
        return super().create(request, *args, **kwargs)
    """
