from rest_framework import viewsets, permissions
from .models import Customer
from .serializers import CustomerSerializer

from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # In een echte app zou je hier 'IsAuthenticated' toevoegen
