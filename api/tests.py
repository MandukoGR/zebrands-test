from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product

""" Product creation test case. """
class ProductCreationTestCase(APITestCase):
    def setUp(self):
        """Set up the test case with a user and access token."""
        self.user = User.objects.create_user(
            username='admin', password='admin', email="admin@test.com", first_name='Admin', last_name='User')

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

""" Product list test case. """
class ProductListTestCase(APITestCase):
    def setUp(self):
        """Create 10 products for testing."""
        Product.objects.create(name='Product 1', price=100.00, brand='Brand A')
        Product.objects.create(name='Product 2', price=150.00, brand='Brand B')
        Product.objects.create(name='Product 3', price=200.00, brand='Brand C')
        Product.objects.create(name='Product 4', price=250.00, brand='Brand D')
        Product.objects.create(name='Product 5', price=300.00, brand='Brand E')
        Product.objects.create(name='Product 6', price=350.00, brand='Brand F')
        Product.objects.create(name='Product 7', price=400.00, brand='Brand G')
        Product.objects.create(name='Product 8', price=450.00, brand='Brand H')
        Product.objects.create(name='Product 9', price=500.00, brand='Brand I')
        Product.objects.create(name='Product 10', price=550.00, brand='Brand J')

    def test_list_products(self):
        """Test listing all products."""
        url = reverse('list_products')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)
    
    def test_pagination(self):
        """Test pagination of products."""
        url = reverse('list_products') + '?page_size=5'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
    
    def test_invalid_parameters(self):
        """Test invalid page number parameter."""
        url = reverse('list_products') + '?page=abc'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_product_empty(self):
        """Test listing products when there are no products."""
        Product.objects.all().delete()
        url = reverse('list_products')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

""" Product detail test case. """
class ProductDetailTestCase(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(
            sku="e4c0ce55-9a2b-44a7-b983-e1c875235134",
            name="Test Product",
            price=100.00,
            brand="Test Brand",
            views=0
        )

        self.user = User.objects.create_user(username='testuser', password='testpass', email='testuser@test.com', first_name='Test', last_name='User')
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def authenticate(self):
        """Authenticate the test client with the user's access token."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    def test_get_product_details_authenticated_user(self):
        """
        Test accessing product details as an authenticated user
        should not increment views.
        """
        self.authenticate()
        url = reverse('product_detail', args=[self.product.sku])
        response = self.client.get(url)

        self.product.refresh_from_db()  
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.product.views, 0)

    def test_get_product_details_unauthenticated_user(self):
        """
        Test accessing product details as an unauthenticated user
        should increment views.
        """
        url = reverse('product_detail', args=[self.product.sku])
        response = self.client.get(url)

        self.product.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.product.views, 1)


""" Product update test case. """
class ProductUpdateTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='password',
            email='admin@test.com',
            first_name='Admin',
            last_name='User'
        )
        self.product = Product.objects.create(
            name='Test Product',
            price=100.0,
            brand='Test Brand'
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(refresh.access_token)


    def authenticate(self):
        """Authenticate the test client with the user's access token."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_update_product(self):
        """Test updating a product."""
        self.authenticate()
        url = reverse('update_product', args=[self.product.sku])
        data = {
            "name": "Updated Product",
            "price": 200.0,
            "brand": "Updated Brand"
        }
        response = self.client.put(url, data, format='json')
        self.product.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.product.name, 'Updated Product')
        self.assertEqual(self.product.price, Decimal('200.0').quantize(Decimal('0.01')))
        self.assertEqual(self.product.brand, 'Updated Brand')

    def test_update_product_invalid_data(self):
        """Test updating a product with invalid data."""
        self.authenticate()
        url = reverse('update_product', args=[self.product.sku])
        data = {
            "name": "Updated Product",
            "price": "invalid",
            "brand": "Updated Brand"
        }
        response = self.client.put(url, data, format='json')
        self.product.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, Decimal('100.0').quantize(Decimal('0.01')))
        self.assertEqual(self.product.brand, 'Test Brand')

    def test_update_product_unauthenticated_user(self):
        """Test updating a product by an unauthenticated user."""
        url = reverse('update_product', args=[self.product.sku])
        data = {
            "name": "Updated Product",
            "price": 200.0,
            "brand": "Updated Brand"
        }
        response = self.client.put(url, data, format='json')
        self.product.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.price, Decimal('100.0').quantize(Decimal('0.01')))
        self.assertEqual(self.product.brand, 'Test Brand')
    
    def test_update_product_not_found(self):
        """Test updating a product that does not exist."""
        self.authenticate()
        url = reverse('update_product', args=['023b8c6b-afa8-4b27-8522-b9f866adb458'])
        data = {
            "name": "Updated Product",
            "price": 200.0,
            "brand": "Updated Brand"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class ProductDeleteTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='password',
            email='admin@test.com',
            first_name='Admin',
            last_name='User'
        )
        self.product = Product.objects.create(
            sku='023b8c6b-afa8-4b27-8522-b9f866adb458',
            name='Test Product',
            price=100.0,
            brand='Test Brand'
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(refresh.access_token)


    def authenticate(self):
        """Authenticate the test client with the user's access token."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_delete_product_success(self):
        """
        Test that an admin can delete a product successfully.
        """
        url = reverse('delete_product', kwargs={'sku': self.product.sku})
        self.authenticate()
        
        response = self.client.delete(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK) 
        self.assertFalse(Product.objects.filter(sku=self.product.sku).exists()) 

    def test_delete_product_unauthenticated(self):
        """
        Test that an unauthenticated user cannot delete a product.
        """
        url = reverse('delete_product', kwargs={'sku': self.product.sku})
        
        response = self.client.delete(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Product.objects.filter(sku=self.product.sku).exists())

    def test_delete_product_not_found(self):
        """
        Test that a product that does not exist cannot be deleted.
        """
        url = reverse('delete_product', kwargs={'sku': 'e4c0ce55-9a2b-44a7-b983-e1c875235134'})
        self.authenticate()
        
        response = self.client.delete(url, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Product.objects.filter(sku=self.product.sku).exists())

    
class CreateAdminUsersTestCase(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            password='password',
            email='admin@example.com',
            first_name='Admin',
            last_name='User'
        )
        refresh = RefreshToken.for_user(self.admin_user)
        self.access_token = str(refresh.access_token)

    def authenticate(self):
        """Authenticate the test client with the user's access token."""
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
    
    def test_create_admin_users(self):
        """Test creating an admin user."""
        self.authenticate()
        url = reverse('create_admin_users')
        data = {
            "username": "newadmin",
            "password": "password",
            "email": "new_admin@example.com",
            "first_name": "New",
            "last_name": "Admin"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newadmin').exists())

    def test_create_admin_users_unauthenticated(self):
        """Test creating an admin user by an unauthenticated user."""
        url = reverse('create_admin_users')
        data = {
            "username": "newadmin",
            "password": "password",
            "email": "new_admin@example.com",
            "first_name": "New",
            "last_name": "Admin"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(User.objects.filter(username='newadmin').exists())

    def test_create_admin_invalid_data(self):
        """Test creating an admin user with invalid data."""
        self.authenticate()
        url = reverse('create_admin_users')
        data = {
            "username": "",
            "password": "password",
            "email": "new_admin@example.com",
            "first_name": "New",
            "last_name": "Admin"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='newadmin').exists())

    def test_create_admin_duplicate_username(self):
        """Test creating an admin user with a duplicate username."""
        self.authenticate()
        url = reverse('create_admin_users')
        data = {
            "username": "admin",
            "password": "password",
            "email": "new_admin@example.com",
            "first_name": "New",
            "last_name": "Admin"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(
            username='newadmin').exists())
        self.assertTrue(User.objects.filter(username='admin').exists())

    def test_create_admin_duplicate_email(self):
        """Test creating an admin user with a duplicate email."""
        self.authenticate()
        url = reverse('create_admin_users')
        data = {
            "username": "newadmin",
            "password": "password",
            "email": "admin@example.com",
            "first_name": "New",
            "last_name": "Admin"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='newadmin').exists())

