from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Internal Identity System
    path('accounts/', include('accounts.urls')),
    
    # HTML Interface (Visual Verification)
    path('projects/', include('projects.urls')),
    
    # EXTERNAL API INTERFACE
    # Access: http://127.0.0.1:8000/api/projects/
    path('api/projects/', include('projects.api_urls')),
]