from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order

@receiver(post_save, sender=Order)
def order_status_change_handler(sender, instance, created, **kwargs):
    if not created:
        # Hier kun je logica toevoegen die draait bij een UPDATE
        print(f"Bestelling {instance.id} is nu: {instance.status}")
        # Toekomst: Stuur hier een Push Notification naar de React Native app
