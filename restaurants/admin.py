from django.contrib import admin
from .models import Restaurant, MenuItem

class MenuItemInline(admin.TabularInline):
    """Hiermee kun je gerechten direct toevoegen op de pagina van het restaurant"""
    model = MenuItem
    extra = 1

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    inlines = [MenuItemInline]

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'price')
    list_filter = ('restaurant',)
