from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'store', 'price', 'stock_quantity', 'is_available', 'created_at')
    list_filter = ('is_available', 'store', 'created_at')
    search_fields = ('name', 'description', 'sku')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Основная информация', {
            'fields': ('store', 'name', 'description', 'sku')
        }),
        ('Цена и наличие', {
            'fields': ('price', 'stock_quantity', 'is_available')
        }),
        ('Изображение', {
            'fields': ('image',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )
