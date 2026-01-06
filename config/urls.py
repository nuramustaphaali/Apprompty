from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 1. Configure the Schema View
schema_view = get_schema_view(
   openapi.Info(
      title="Apprompty API",
      default_version='v1',
      description="API documentation for the AI Architect System",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@apprompty.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('projects/', include('projects.urls')),
    path('api/projects/', include('projects.api_urls')),

    # 2. Add Documentation URLs
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]