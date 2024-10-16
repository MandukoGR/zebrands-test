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
        fields = ["id", "username", "password", "email", "first_name", "last_name"]

    def create(self, validated_data):
        """
        Create a new user instance.
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", "")
        )
        return user
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value


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
