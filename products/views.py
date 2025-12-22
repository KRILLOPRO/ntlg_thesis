from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product
from .serializers import ProductSerializer, ProductDetailSerializer
from stores.models import Store


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для работы с товарами"""
    queryset = Product.objects.select_related('store').filter(is_available=True)
    serializer_class = ProductSerializer
    permission_classes = []  # Разрешаем просмотр товаров без авторизации
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['store', 'is_available']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    @action(detail=True, methods=['get'])
    def specification(self, request, pk=None):
        """Получение спецификации товара"""
        product = self.get_object()
        serializer = ProductDetailSerializer(product)
        
        # Дополнительная информация для спецификации
        specification_data = serializer.data
        specification_data['store_info'] = {
            'name': product.store.name,
            'address': product.store.address,
            'phone': product.store.phone,
            'email': product.store.email,
        }
        specification_data['availability'] = {
            'is_available': product.is_available,
            'stock_quantity': product.stock_quantity,
            'is_in_stock': product.is_in_stock(),
            'can_be_ordered': product.can_be_ordered(1),
        }
        
        return Response(specification_data)
