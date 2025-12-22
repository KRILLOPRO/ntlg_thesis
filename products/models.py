from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from stores.models import Store


class Product(models.Model):
    """Модель товара"""
    store = models.ForeignKey(
        Store,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='Магазин'
    )
    name = models.CharField(max_length=300, verbose_name='Название товара')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    sku = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Артикул',
        help_text='Уникальный идентификатор товара'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Цена'
    )
    image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )
    is_available = models.BooleanField(default=True, verbose_name='Доступен для заказа')
    stock_quantity = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество на складе'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['store', 'is_available']),
            models.Index(fields=['sku']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.store.name})"
    
    def is_in_stock(self):
        """Проверяет наличие товара на складе"""
        return self.stock_quantity > 0 and self.is_available
    
    def can_be_ordered(self, quantity=1):
        """Проверяет, можно ли заказать указанное количество товара"""
        return self.is_available and self.stock_quantity >= quantity
