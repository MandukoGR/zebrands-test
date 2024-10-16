from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product


class ProductCreationTestCase(APITestCase):
    def setUp(self):
        """Set up the test case with a user and access token."""
        self.user = User.objects.create_user(
            username='admin', password='admin', email="admin@test.com")

        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

        self.url = reverse('create_product')

    def authenticate(self):
        """Authenticate the test client with the user's access token."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_create_product_with_all_fields(self):
        """Test product creation with all required fields (name, price, brand)."""
        self.authenticate()

        data = {
            "name": "Test Product",
            "price": 199.99,
            "brand": "Test Brand"
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().name, 'Test Product')
        self.assertEqual(Product.objects.get().price, Decimal(
            '199.99').quantize(Decimal('0.01')))
        self.assertEqual(Product.objects.get().brand, 'Test Brand')

    def test_create_product_with_missing_fields(self):
        """Test product creation with missing required fields."""
        self.authenticate()

        data = {
            "name": "Test Product",
            "brand": "Test Brand"
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Product.objects.count(), 0)

    def test_create_product_invalid_format(self):
        """Test product creation with invalid price format."""
        self.authenticate()

        data = {
            "name": "Test Product",
            "price": "invalid",
            "brand": "Test Brand"
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Product.objects.count(), 0)

    def test_success_message_and_product_info(self):
        """Test success message and product info in response."""
        self.authenticate()

        data = {
            "name": "Test Product",
            "price": 199.99,
            "brand": "Test Brand"
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'],
                         'Product created successfully')
        self.assertEqual(response.data['product']['name'], 'Test Product')
        self.assertEqual(response.data['product']['price'], '199.99')
        self.assertEqual(response.data['product']['brand'], 'Test Brand')

    def test_unauthenticated_user(self):
        """Test product creation by unauthenticated user."""
        data = {
            "name": "Test Product",
            "price": 199.99,
            "brand": "Test Brand"
        }

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Product.objects.count(), 0)
