from rest_framework import serializers
from .models import UrlModel


class UrlModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlModel
        exclude = ['access_count']


class UrlStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlModel
        fields = "__all__"