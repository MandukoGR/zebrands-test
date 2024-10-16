from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Product


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


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model.
    Converts Product model instances to JSON format and vice versa.
    """

    class Meta(object):
        """
        Meta class to specify the model and fields to be used in the serializer.
        """
        model = Product
        fields = ["sku", "name", "brand", "price", "views"]

        def validate(self, data):
            """
            Validate the data before saving.
            """
            if 'price' in data and data['price'] <= 0:
                raise serializers.ValidationError(
                    "Price must be a positive value.")
            return data
