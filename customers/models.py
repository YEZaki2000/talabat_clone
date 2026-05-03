from django.contrib.auth.models import AbstractUser
from django.db import models

class Customer(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=50, default="Cairo")

    def __str__(self):
        return self.username
