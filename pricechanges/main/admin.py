from django.contrib import admin
from .models import Items, Marketplace, TagItem

admin.site.site_header = 'Панель администрирования'
admin.site.index_title = 'Отслеживание цен на маркетплейсах'

@admin.register(Items)
class MainAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'time_create', 'mtplace')
    list_display_links = ('name',)
    ordering = ('time_create', 'id')
    list_editable = ('brand', 'mtplace')
    list_per_page = 10
    search_fields = ('name',)
    list_filter = ('mtplace',)
    readonly_fields = ('slug',)

@admin.register(Marketplace)
class MarketplaceAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)

@admin.register(TagItem)
class TagAdmin(admin.ModelAdmin):
    list_display = ('tag',)
    list_display_links = ('tag',)
