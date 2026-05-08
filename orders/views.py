from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer
from .permissions import IsOwner
from django.db import transaction
from rest_framework.decorators import action

from rest_framework import permissions

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all().order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def perform_create(self, serializer):
        # Koppel de ingelogde gebruiker automatisch aan de bestelling
        serializer.save(customer=self.request.user)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()

        # Check of de bestelling al niet geleverd of geannuleerd is
        if order.status in ['DELIVERED', 'CANCELLED']:
            return Response(
                {"error": f"Bestelling kan niet geannuleerd worden met status {order.status}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Voorraad teruggeven
            for item in order.items.all():
                menu_item = item.menu_item
                menu_item.stock += item.quantity
                menu_item.save()

            # Status bijwerken
            order.status = 'CANCELLED'
            order.save()

        return Response({"status": "Bestelling geannuleerd en voorraad hersteld."})

    """
    def create(self, request, *args, **kwargs):
        \"""Aangepaste create om ook OrderItems in één keer te verwerken\"""
        return super().create(request, *args, **kwargs)
    """
