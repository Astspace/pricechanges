from django.urls import path
from . import views


urlpatterns = [
    path('', views.HomeItems.as_view(), name='home'),
    path('add_item_error/', views.AddItemError.as_view(), name='add_item_error'),
    path('add_item/', views.AddItem.as_view(), name='add_item'),
    path('update_item/<int:pk>/', views.UpdateItem.as_view(), name='update_item'),
    path('contact/', views.contact, name='contact'),
    path('items/<slug:item_slug>/', views.ShowItem.as_view(), name='item'),
    path('marketplace/<slug:mtplace_slug>/', views.ShowMenu.as_view(), name='marketplace'),
    path('tag/<slug:tag_slug>/', views.ShowTagItems.as_view(), name='tag'),
]
