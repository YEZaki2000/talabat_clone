from django.db import models
from django.conf import settings
from restaurants.models import Restaurant, MenuItem

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PREPARING', 'Preparing'),
        ('ON_THE_WAY', 'On the way'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]

    PAYMENT_METHODS = [
        ('CASH', 'Cash on Delivery'),
        ('TALABAT_PAY', 'Talabat Pay (Wallet)'),
        ('CREDIT_CARD', 'Credit Card'),
        ('POSTPAID', 'PostPaid (Pay Later)'),
    ]

    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHODS, 
        default='CASH'
    )
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS, 
        default='PENDING'
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_total_price(self):
        # Bereken de som van (prijs_per_stuk * aantal) voor alle items
        total = sum(item.quantity * item.price_at_order for item in self.items.all())
        self.total_price = total
        # Gebruik update_fields om te voorkomen dat de save() methode een loop veroorzaakt
        self.save(update_fields=['total_price'])

    def __str__(self):
        return f"Order {self.id} by {self.customer.username if self.customer else 'Unknown'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_at_order = models.DecimalField(max_digits=10, decimal_places=2) # Prijs vastleggen op moment van bestellen

    def save(self, *args, **kwargs):
        # Pak automatisch de prijs van het menu_item als deze nog niet is ingesteld
        if not self.price_at_order:
            self.price_at_order = self.menu_item.price
        super().save(*args, **kwargs)
        
        # Update daarna de totaalprijs van de moeder-bestelling
        self.order.update_total_price()

    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

class OrderStatusLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='logs')
    status = models.CharField(max_length=20)
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.order.id} moved to {self.status}"
