from rest_framework import serializers

from api import models


class CemeteryRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CemeteryRegister
        fields = '__all__'


class ObituaryNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ObituaryNotice
        fields = '__all__'
