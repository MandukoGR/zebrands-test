from django.urls import re_path
from api import views
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Product API",
        default_version='v1',
        description="API for managing catalogue of products",
        contact=openapi.Contact(email="ar.gutierrezrojo@gmail.com"),
    ),
    public=True,
)
urlpatterns = [
    re_path('login', views.login, name='login'),
    re_path('catalogue', views.list_products, name='list_products'),
    re_path('product/(?P<sku>[^/]+)/$', views.product_detail, name='product_detail'),  
    re_path('updateproduct/(?P<sku>[^/]+)', views.update_product, name='update_product'), 
    re_path('deleteproduct/(?P<sku>[^/]+)', views.delete_product, name='delete_product'),
    re_path('refresh_token', views.refresh_token, name='refresh_token'),
    re_path('newproduct', views.create_product, name='create_product'),
    re_path('newadmin', views.create_admin_users, name='create_admin_users'),
    re_path('admins', views.list_admin_users, name='list_admin_users'),
    re_path('updateadmin/(?P<id>[^/]+)', views.update_admin_user, name='update_admin_user'),
    re_path('deleteadmin/(?P<id>[^/]+)', views.delete_admin_user, name='delete_admin_user'),

    # Swagger UI
    re_path('swagger(?P<format>\.json|\.yaml)', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
  
]



