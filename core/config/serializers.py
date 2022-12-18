from rest_framework import serializers


class IdListSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())
