from api.models import Product, ProductPagination
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication


from .serializers import ProductSerializer, UserSerializer
import re
from django.core.mail import send_mail
from django.conf import settings


@api_view(["POST"])
def login(request):
    """
    Handle user login and return JWT tokens.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"detail": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    user = get_object_or_404(User, username=username)
    
    if not user.check_password(password):
        return Response({"detail": "Incorrect username or password"}, status=status.HTTP_404_NOT_FOUND)

    refresh = RefreshToken.for_user(user)

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }, status=status.HTTP_200_OK)


@api_view(["POST"])
def signup(request):
    """
    Handle user signup and return JWT tokens.
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"detail": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        user.set_password(password)  # Ensures password is hashed
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    """
    Test JWT token authentication.
    """
    return Response("You are authenticated {}".format(request.user.email), status=status.HTTP_200_OK)


@api_view(["POST"])
def refresh_token(request):
    """
    Handle refresh token and return new access token.
    """
    refresh_token = request.data.get("refresh")
    if not refresh_token:
        return Response({"detail": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token

        return Response({
            'access': str(access_token)
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(["POST"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def create_product(request):
    """
    Create a new product.
    """
    serializer = ProductSerializer(data=request.data)
    
    if serializer.is_valid():
        product = serializer.save()
        return Response({
            "message": "Product created successfully",
            "product": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def product_detail(request, sku):
    """
    Retrieve a product by SKU.
    """
    try:
        product = get_object_or_404(Product, sku=sku)

        # Increment the views count only if user is not authenticated
        if not request.user.is_authenticated:
            product.views += 1
            product.save()

        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(["PUT"])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def update_product(request, sku):
    """
    Update a product by SKU.
    """
    try:
        product = Product.objects.get(sku=sku)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        
        users = User.objects.all()
        recipient_list = [user.email for user in users if user.email]

        send_mail(
            subject="Product Updated",
            message=f"The product {product.name} has been updated. New details: {serializer.data}",
            from_email=settings.DEFAULT_FROM_EMAIL,  
            recipient_list=recipient_list,
            fail_silently=False,
        )

        return Response({
            "message": "Product updated successfully",
            "product": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(["GET"])
def list_products(request):
    """
    List all products paginated.
    """
    try:
        products = Product.objects.all()
        paginator = ProductPagination()
        paginated_products = paginator.paginate_queryset(products, request)
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)
    except:
        return Response({"detail": "Incorrect query parameters" }, status=status.HTTP_400_BAD_REQUEST)



