from rest_framework import serializers
from .models import Store


class StoreSerializer(serializers.ModelSerializer):
    """Сериализатор для магазина"""
    active_products_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Store
        fields = (
            'id', 'name', 'description', 'address', 'phone', 
            'email', 'is_active', 'active_products_count', 
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def to_representation(self, instance):
        """Добавляем вычисляемое поле active_products_count"""
        representation = super().to_representation(instance)
        representation['active_products_count'] = instance.get_active_products_count()
        return representation

