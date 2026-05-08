from rest_framework import serializers
from .models import Order, OrderItem
from restaurants.models import MenuItem
from restaurants.serializers import MenuItemSerializer
from django.db import transaction

class OrderItemSerializer(serializers.ModelSerializer):
    # We voegen de details van het menu_item toe voor de frontend
    menu_item_details = MenuItemSerializer(source='menu_item', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'menu_item', 'menu_item_details', 'quantity', 'price_at_order']

# Order Serializer
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
            'created_at', 'items', 'items_input', 'payment_method',
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items_input', [])
        
        # We gebruiken hier de atomic transactie
        with transaction.atomic():
            # 1. Maak de Order aan
            order = Order.objects.create(**validated_data)
            
            for item in items_data:
                m_item_id = item.get('menu_item')
                qty = item.get('quantity', 1)
                
                # Gebruik select_for_update() om de voorraad te 'locken'
                try:
                    menu_item_obj = MenuItem.objects.select_for_update().get(id=m_item_id)
                    
                    # PROFESSIONELE CHECK: Is er genoeg voorraad?
                    if menu_item_obj.stock < qty:
                        raise serializers.ValidationError(
                            f"Niet genoeg voorraad voor {menu_item_obj.name}. Beschikbaar: {menu_item_obj.stock}"
                        )
                    
                    # Verlaag de voorraad
                    menu_item_obj.stock -= qty
                    menu_item_obj.save()

                    OrderItem.objects.create(
                        order=order, 
                        menu_item=menu_item_obj, 
                        quantity=qty,
                        price_at_order=menu_item_obj.price # Leg de prijs vast!
                    )
                except MenuItem.DoesNotExist:
                    raise serializers.ValidationError(f"Menu item met ID {m_item_id} bestaat niet.")
            
            # 2. Bereken totaalprijs
            order.update_total_price()
            return order       

    def validate(self, data):
        restaurant = data.get('restaurant')
        items_input = data.get('items_input', [])
        # stock = data.get

        # 1. Check of het restaurant actief is
        if not restaurant.is_active:
            raise serializers.ValidationError(
                {"restaurant": "Dit restaurant neemt momenteel geen bestellingen aan."}
            )

        # 2. Check of er wel items zijn meegegeven
        if not items_input:
            raise serializers.ValidationError(
                {"items_input": "Je kunt geen lege bestelling plaatsen."}
            )

        # 3. Validatie van de menu-items
                
        for item in items_input:
            menu_item_id = item.get('menu_item')
            quantity = item.get('quantity', 0)

            # Check of quantity wel positief is
            if quantity <= 0:
                raise serializers.ValidationError(
                    {"items_input": f"Aantal voor item {menu_item_id} moet groter zijn dan 0."}
                )

            try:
                menu_item = MenuItem.objects.get(id=menu_item_id)
                
                # CRUCIAL: Hoort dit gerecht wel bij het gekozen restaurant?
                if menu_item.restaurant != restaurant:
                    raise serializers.ValidationError(
                        {"items_input": f"Item '{menu_item.name}' hoort niet bij restaurant '{restaurant.name}'."}
                    )

                # Check 2: Is er genoeg voorraad?
                if menu_item.stock < quantity:
                    raise serializers.ValidationError(
                        f"Helaas, er zijn nog maar {menu_item.stock} porties van {menu_item.name} beschikbaar."
                    )
            
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError(
                    {"items_input": f"Menu-item met ID {menu_item_id} bestaat niet."}
                )

        return data
