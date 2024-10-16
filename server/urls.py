from django.urls import re_path
from api import views

urlpatterns = [
    re_path('login', views.login, name='login'),
    re_path('signup', views.signup, name='signup'),
    re_path('catalogue', views.list_products, name='list_products'),
    re_path('product/(?P<sku>[^/]+)/$', views.product_detail, name='product_detail'),  # Product detail URL
    re_path('updateproduct/(?P<sku>[^/]+)', views.update_product, name='update_product'),  # Update product URL
    re_path('deleteproduct/(?P<sku>[^/]+)', views.delete_product, name='delete_product'),  # Delete product URL
    re_path('refresh_token', views.refresh_token, name='refresh_token'),
    re_path('newproduct', views.create_product, name='create_product'),
  
]



