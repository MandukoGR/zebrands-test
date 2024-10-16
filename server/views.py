from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenRefreshView

from .serializers import UserSerializer


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
    serializer = UserSerializer(instance=user)

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


# Refresh token view
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