from django.urls import path
from . import views


urlpatterns = [
    path('', views.HomeItems.as_view(), name='home'),
    path('about/', views.About.as_view(), name='about'),
    path('add_item/', views.AddItem.as_view(), name='add_item'),
    path('update_item/<int:pk>/', views.UpdateItem.as_view(), name='update_item'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('items/<slug:item_slug>/', views.ShowItem.as_view(), name='item'),
    path('marketplace/<slug:mtplace_slug>/', views.show_menu, name='marketplace'),
    path('tag/<slug:tag_slug>/', views.show_tag_items, name='tag'),
]
