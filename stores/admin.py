from django.contrib import admin
from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'get_active_products_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description', 'address')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Контакты', {
            'fields': ('address', 'phone', 'email')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
