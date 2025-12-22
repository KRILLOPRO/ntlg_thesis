from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegisterView, login_view, UserProfileView

app_name = 'users'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', login_view, name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]

