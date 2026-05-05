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
    items_input = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )
    customer_name = serializers.ReadOnlyField(source='customer.username')
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')

    class Meta:
        model = Order
        fields = [
            'id', 'customer', 'customer_name', 'restaurant', 
            'restaurant_name', 'status', 'total_price', 
            'created_at', 'items', 'items_input'
        ]

    def create(self, validated_data):
        # 1. Haal de items_input eruit. 
        # Als we dit niet doen, probeert Django 'items_input' in de Order-tabel te zetten -> CRASH.
        items_data = validated_data.pop('items_input', [])
        
        # 2. Maak de Order aan met de overgebleven data (restaurant, status, customer, etc.)
        order = Order.objects.create(**validated_data)
        
        # 3. Maak de OrderItems aan
        for item in items_data:
            m_item_id = item.get('menu_item')
            qty = item.get('quantity', 1)
            
            try:
                from restaurants.models import MenuItem
                menu_item_obj = MenuItem.objects.get(id=m_item_id)
                OrderItem.objects.create(
                    order=order, 
                    menu_item=menu_item_obj, 
                    quantity=qty
                )
            except MenuItem.DoesNotExist:
                continue # Of geef een foutmelding
        
        # 4. Bereken totaalprijs en ververs voor de response
        order.update_total_price()
        order.refresh_from_db()
        return order

        

    def validate(self, data):
        restaurant = data.get('restaurant')
        if not restaurant.is_active:
            raise serializers.ValidationError("Dit restaurant neemt momenteel geen bestellingen aan.")
        return data
