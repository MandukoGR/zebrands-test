from django.urls import re_path
from api import views

urlpatterns = [
    re_path('login', views.login, name='login'),
    re_path('signup', views.signup, name='signup'),
    re_path('test_token', views.test_token, name='test_token'),
    re_path('refresh_token', views.refresh_token, name='refresh_token'),
    re_path('products', views.create_product, name='create_product'),
]


