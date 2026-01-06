from django.urls import path
from django.contrib.auth import views as auth_views
from . import views, api_views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # --- API Endpoints (For the App) ---
    path('api/register/', api_views.RegisterAPIView.as_view(), name='api_register'),
    path('api/login/', obtain_auth_token, name='api_token_auth'), # Returns Token

    # --- HTML Views (For verification) ---
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]