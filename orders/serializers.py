from rest_framework import serializers
from .models import Order, OrderItem
from restaurants.serializers import MenuItemSerializer

class OrderItemSerializer(serializers.ModelSerializer):
    # We voegen de details van het menu_item toe voor de frontend
    menu_item_details = MenuItemSerializer(source='menu_item', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_details', 'quantity', 'price_at_order']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.username')
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'restaurant', 
            'restaurant_name', 'status', 'total_price', 
            'created_at', 'items'
        ]
