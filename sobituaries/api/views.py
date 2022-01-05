from rest_framework import filters
from rest_framework import generics

from api import models
from api import serializers


class CemeteryRegisterView(generics.ListCreateAPIView):
    queryset = models.CemeteryRegister.objects.all()
    serializer_class = serializers.CemeteryRegisterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ['title', 'description']
