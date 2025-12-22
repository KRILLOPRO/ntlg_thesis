from rest_framework import serializers
from .models import Product
from stores.serializers import StoreSerializer


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор для товара"""
    store = StoreSerializer(read_only=True)
    store_id = serializers.IntegerField(write_only=True, required=False)
    is_in_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = (
            'id', 'store', 'store_id', 'name', 'description', 'sku', 
            'price', 'image', 'is_available', 'stock_quantity', 
            'is_in_stock', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Добавляем вычисляемое поле is_in_stock"""
        representation = super().to_representation(instance)
        representation['is_in_stock'] = instance.is_in_stock()
        return representation


class ProductDetailSerializer(ProductSerializer):
    """Расширенный сериализатор для детального просмотра товара"""
    pass

