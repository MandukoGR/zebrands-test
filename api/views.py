from api.models import Product, ProductPagination
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import ProductSerializer, UserSerializer
import re
from django.core.mail import send_mail
from django.conf import settings

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password'),
        }
    ),
    responses={200: 'JWT tokens returned', 400: 'Bad Request', 404: 'Not Found'}
)
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


@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    responses={201: 'User created and JWT tokens returned', 400: 'Bad Request'}
)
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


@swagger_auto_schema(
    method='get',
    responses={200: 'Authenticated', 401: 'Unauthorized'},
    security=[{'Bearer': []}]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def test_token(request):
    """
    Test JWT token authentication.
    """
    return Response("You are authenticated {}".format(request.user.email), status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
        }
    ),
    responses={200: 'New access token returned', 400: 'Bad Request'}
)
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
    

@swagger_auto_schema(
    method='post',
    request_body=ProductSerializer,
    responses={201: 'Product created successfully', 400: 'Bad Request'},
    security=[{'Bearer': []}]
)
@api_view(["POST"])
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


@swagger_auto_schema(
    method='get',
    responses={200: ProductSerializer, 404: 'Product not found'}
)
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


@swagger_auto_schema(
    method='put',
    request_body=ProductSerializer,
    responses={200: 'Product updated successfully', 400: 'Bad Request', 404: 'Product not found'},
    security=[{'Bearer': []}]
)
@api_view(["PUT"])
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


@swagger_auto_schema(
    method='delete',
    responses={200: 'Product deleted successfully', 404: 'Product not found'},
    security=[{'Bearer': []}]
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_product(request, sku):
    """
    Delete a product by SKU.
    """
    try:
        product = Product.objects.get(sku=sku)
        product.delete()
        return Response({"message": "Product deleted successfully"}, status=status.HTTP_200_OK)
    except Product.DoesNotExist:
        return Response({"detail": "Product not found"}, status=status.HTTP_404_NOT_FOUND)


@swagger_auto_schema(
    method='get',
    responses={200: ProductSerializer(many=True), 400: 'Incorrect query parameters'}
)
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


@swagger_auto_schema(
    method='post',
    request_body=UserSerializer,
    responses={201: 'Admin user created successfully', 400: 'Bad Request'},
    security=[{'Bearer': []}]
)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_admin_users(request):
    """
    Create admin users.
    """
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")
    first_name = request.data.get("first_name")
    last_name = request.data.get("last_name")

    if not username or not password or not email or not first_name or not last_name:
        return Response({"detail": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = UserSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        user.is_staff = True
        user.save()
        return Response({
            "message": "Admin user created successfully",
            "user": serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='get',
    responses={200: UserSerializer(many=True)},
    security=[{'Bearer': []}]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_admin_users(request):
    """
    List all admin users.
    """
    users = User.objects.all().values("id", "username", "password", "email", "first_name", "last_name")
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='put',
    request_body=UserSerializer,
    responses={200: 'User updated successfully', 400: 'Bad Request', 404: 'User not found'},
    security=[{'Bearer': []}]
)
@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_admin_user(request, id):
    """
    Update an admin user by ID.
    """
    try:
        user = User.objects.get(id=id)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = UserSerializer(user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            "message": "User updated successfully",
            "user": serializer.data
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='delete',
    responses={200: 'User deleted successfully', 404: 'User not found'},
    security=[{'Bearer': []}]
)
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_admin_user(request, id):
    """
    Delete an admin user by ID.
    """
    try:
        user = User.objects.get(id=id)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)
