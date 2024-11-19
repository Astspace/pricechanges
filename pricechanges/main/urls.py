from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('about/', views.about, name='about'),
    path('add_item/', views.add_item, name='add_item'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('items/<slug:item_slug>/', views.show_item, name='item'),
    path('marketplace/<slug:mtplace_slug>/', views.show_menu, name='marketplace'),
    path('tag/<slug:tag_slug>/', views.show_tag_items, name='tag'),
]
