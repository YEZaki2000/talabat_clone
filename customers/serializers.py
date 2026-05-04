from rest_framework import serializers
from .models import Customer

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Voeg je eigen velden toe aan de "payload" van het token
        token['username'] = user.username
        token['city'] = user.city
        token['address'] = user.address
        token['is_staff'] = user.is_staff

        return token

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'username', 'email', 'phone_number', 'address', 'city']
