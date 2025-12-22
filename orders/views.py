from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from .models import Order, OrderItem, DeliveryAddress
from .serializers import (
    OrderSerializer, OrderCreateSerializer, OrderStatusUpdateSerializer,
    OrderItemSerializer, DeliveryAddressSerializer
)
from products.models import Product
from .tasks import send_order_confirmation_email


class DeliveryAddressViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с адресами доставки"""
    serializer_class = DeliveryAddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartViewSet(viewsets.ViewSet):
    """ViewSet для работы с корзиной (неподтвержденными заказами)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_cart_order(self):
        """Получает или создает корзину (заказ со статусом pending)"""
        order, created = Order.objects.get_or_create(
            user=self.request.user,
            status='pending',
            defaults={'total_amount': 0}
        )
        return order
    
    @action(detail=False, methods=['get'])
    def items(self, request):
        """Получение списка товаров в корзине"""
        order = self.get_cart_order()
        items = order.items.all()
        serializer = OrderItemSerializer(items, many=True)
        return Response({
            'order_id': order.id,
            'total_amount': order.total_amount,
            'items': serializer.data
        })
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """Добавление товара в корзину"""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        if not product_id:
            return Response(
                {'error': 'Не указан product_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id, is_available=True)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Товар не найден или недоступен'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not product.can_be_ordered(quantity):
            return Response(
                {'error': f'Недостаточно товара на складе. Доступно: {product.stock_quantity}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order = self.get_cart_order()
        
        # Проверяем, есть ли уже этот товар в корзине
        order_item, created = OrderItem.objects.get_or_create(
            order=order,
            product=product,
            defaults={'quantity': quantity, 'price': product.price}
        )
        
        if not created:
            # Обновляем количество
            order_item.quantity += quantity
            order_item.save()
        
        # Пересчитываем общую сумму
        order.calculate_total()
        order.save()
        
        serializer = OrderItemSerializer(order_item)
        return Response({
            'message': 'Товар добавлен в корзину',
            'item': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['delete'])
    def remove(self, request):
        """Удаление товара из корзины"""
        item_id = request.data.get('item_id')
        
        if not item_id:
            return Response(
                {'error': 'Не указан item_id'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            order = self.get_cart_order()
            order_item = OrderItem.objects.get(id=item_id, order=order)
            order_item.delete()
            
            # Пересчитываем общую сумму
            order.calculate_total()
            order.save()
            
            return Response({'message': 'Товар удален из корзины'})
        except OrderItem.DoesNotExist:
            return Response(
                {'error': 'Товар не найден в корзине'},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderViewSet(viewsets.ModelViewSet):
    """ViewSet для работы с заказами"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        elif self.action == 'update_status':
            return OrderStatusUpdateSerializer
        return OrderSerializer
    
    @transaction.atomic
    def create(self, request):
        """Создание заказа из корзины"""
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Получаем корзину (pending заказ)
        cart_order = Order.objects.filter(
            user=request.user,
            status='pending'
        ).prefetch_related('items__product').first()
        
        if not cart_order or cart_order.items.count() == 0:
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверяем адрес доставки
        delivery_address_id = serializer.validated_data.get('delivery_address_id')
        if delivery_address_id:
            try:
                delivery_address = DeliveryAddress.objects.get(
                    id=delivery_address_id,
                    user=request.user
                )
            except DeliveryAddress.DoesNotExist:
                return Response(
                    {'error': 'Адрес доставки не найден'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            # Пытаемся найти адрес по умолчанию
            delivery_address = DeliveryAddress.objects.filter(
                user=request.user,
                is_default=True
            ).first()
            
            if not delivery_address:
                return Response(
                    {'error': 'Не указан адрес доставки'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Проверяем наличие всех товаров
        for item in cart_order.items.all():
            if not item.product.can_be_ordered(item.quantity):
                return Response(
                    {
                        'error': f'Товар "{item.product.name}" недоступен в количестве {item.quantity}'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Обновляем заказ
        cart_order.delivery_address = delivery_address
        cart_order.status = 'confirmed'
        cart_order.confirmed_at = timezone.now()
        cart_order.notes = serializer.validated_data.get('notes', '')
        cart_order.calculate_total()
        cart_order.save()
        
        # Отправляем email с подтверждением через Celery
        send_order_confirmation_email.delay(cart_order.id)
        
        return Response(
            OrderSerializer(cart_order).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Обновление статуса заказа (для администраторов)"""
        order = self.get_object()
        
        # Проверяем права доступа (только администратор или владелец заказа)
        if not request.user.is_staff and order.user != request.user:
            return Response(
                {'error': 'Недостаточно прав'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        """Получение списка заказов текущего пользователя"""
        orders = self.get_queryset()
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
