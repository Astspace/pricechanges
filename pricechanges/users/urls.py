from django.urls import path
from . import views


app_name = 'users'

urlpatterns = [
    path('login/', views.LoginUsers.as_view(), name='login'),
    path('logout/', views.logout_users, name='logout'),
    path('register/', views.RegisterUser.as_view(), name='register'),
    path('profile/', views.ProfileUser.as_view(), name='profile'),
    ]
