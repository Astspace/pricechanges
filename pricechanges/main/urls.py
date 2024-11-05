from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('items/<int:item_id>/', views.show_item, name='item'),
    path('menu/<int:menu_id>/', views.show_menu, name='menu'),
]
