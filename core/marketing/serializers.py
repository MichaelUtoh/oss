from cProfile import label
from rest_framework import serializers


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(label="Email", max_length=128)
