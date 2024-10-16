from rest_framework import serializers
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    Converts User model instances to JSON format and vice versa.
    """

    class Meta(object):
        """
        Meta class to specify the model and fields to be used in the serializer.
        """
        model = User
        fields = ["id", "username", "password", "email"]
