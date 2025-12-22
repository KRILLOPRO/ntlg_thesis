from django.contrib import admin
from .models import Order, OrderItem, DeliveryAddress


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('price', 'get_total', 'created_at')
    fields = ('product', 'quantity', 'price', 'get_total', 'created_at')
    
    def get_total(self, obj):
        if obj.pk:
            return obj.get_total()
        return '-'
    get_total.short_description = 'Итого'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'get_items_count', 'created_at', 'confirmed_at')
    list_filter = ('status', 'created_at', 'confirmed_at')
    search_fields = ('user__email', 'user__username', 'id')
    readonly_fields = ('total_amount', 'created_at', 'updated_at', 'confirmed_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'status', 'delivery_address')
        }),
        ('Сумма', {
            'fields': ('total_amount',)
        }),
        ('Примечания', {
            'fields': ('notes',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at', 'confirmed_at')
        }),
    )
    
    def get_items_count(self, obj):
        return obj.get_items_count()
    get_items_count.short_description = 'Позиций'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'get_total', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('order__id', 'product__name')
    readonly_fields = ('price', 'created_at', 'get_total')
    
    def get_total(self, obj):
        return obj.get_total()
    get_total.short_description = 'Итого'


@admin.register(DeliveryAddress)
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_full_address', 'is_default', 'created_at')
    list_filter = ('is_default', 'city', 'created_at')
    search_fields = ('user__email', 'city', 'street', 'house')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'is_default')
        }),
        ('Адрес', {
            'fields': ('city', 'street', 'house', 'apartment', 'postal_code')
        }),
        ('Дата', {
            'fields': ('created_at',)
        }),
    )
