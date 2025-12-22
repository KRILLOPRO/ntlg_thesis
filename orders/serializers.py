from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem, DeliveryAddress
from products.serializers import ProductSerializer


class DeliveryAddressSerializer(serializers.ModelSerializer):
    """Сериализатор для адреса доставки"""
    full_address = serializers.CharField(read_only=True)
    
    class Meta:
        model = DeliveryAddress
        fields = (
            'id', 'user', 'city', 'street', 'house', 'apartment', 
            'postal_code', 'is_default', 'full_address', 'created_at'
        )
        read_only_fields = ('id', 'user', 'created_at')
    
    def to_representation(self, instance):
        """Добавляем вычисляемое поле full_address"""
        representation = super().to_representation(instance)
        representation['full_address'] = instance.get_full_address()
        return representation


class OrderItemSerializer(serializers.ModelSerializer):
    """Сериализатор для позиции заказа"""
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_id', 'quantity', 'price', 'total', 'created_at')
        read_only_fields = ('id', 'price', 'created_at')
    
    def to_representation(self, instance):
        """Добавляем вычисляемое поле total"""
        representation = super().to_representation(instance)
        representation['total'] = instance.get_total()
        return representation


class OrderSerializer(serializers.ModelSerializer):
    """Сериализатор для заказа"""
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address = DeliveryAddressSerializer(read_only=True)
    delivery_address_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    items_count = serializers.IntegerField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Order
        fields = (
            'id', 'user', 'delivery_address', 'delivery_address_id', 
            'status', 'status_display', 'total_amount', 'items', 
            'items_count', 'notes', 'created_at', 'updated_at', 'confirmed_at'
        )
        read_only_fields = (
            'id', 'user', 'total_amount', 'created_at', 
            'updated_at', 'confirmed_at'
        )
    
    def to_representation(self, instance):
        """Добавляем вычисляемые поля"""
        representation = super().to_representation(instance)
        representation['items_count'] = instance.get_items_count()
        return representation


class OrderCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания заказа"""
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        help_text="Список товаров: [{'product_id': 1, 'quantity': 2}, ...]"
    )
    
    class Meta:
        model = Order
        fields = ('delivery_address_id', 'items', 'notes')
    
    def validate_items(self, value):
        """Валидация списка товаров"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("Список товаров не может быть пустым")
        return value


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления статуса заказа"""
    class Meta:
        model = Order
        fields = ('status',)

