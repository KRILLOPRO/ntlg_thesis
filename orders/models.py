from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from users.models import User
from products.models import Product
from stores.models import Store


class DeliveryAddress(models.Model):
    """Модель адреса доставки"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='delivery_addresses',
        verbose_name='Пользователь'
    )
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=200, verbose_name='Улица')
    house = models.CharField(max_length=20, verbose_name='Дом')
    apartment = models.CharField(max_length=20, blank=True, null=True, verbose_name='Квартира')
    postal_code = models.CharField(max_length=20, blank=True, null=True, verbose_name='Почтовый индекс')
    is_default = models.BooleanField(default=False, verbose_name='Адрес по умолчанию')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Адрес доставки'
        verbose_name_plural = 'Адреса доставки'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        address_parts = [self.city, self.street, self.house]
        if self.apartment:
            address_parts.append(f"кв. {self.apartment}")
        return ", ".join(address_parts)
    
    def get_full_address(self):
        """Возвращает полный адрес в виде строки"""
        parts = [self.city, self.street, f"д. {self.house}"]
        if self.apartment:
            parts.append(f"кв. {self.apartment}")
        if self.postal_code:
            parts.append(f"({self.postal_code})")
        return ", ".join(parts)
    
    def save(self, *args, **kwargs):
        """При сохранении адреса как адреса по умолчанию, снимаем флаг с других адресов пользователя"""
        if self.is_default:
            DeliveryAddress.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)


class Order(models.Model):
    """Модель заказа"""
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтвержден'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='Пользователь'
    )
    delivery_address = models.ForeignKey(
        DeliveryAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Адрес доставки'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус заказа'
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Общая сумма заказа'
    )
    notes = models.TextField(blank=True, null=True, verbose_name='Примечания')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    confirmed_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата подтверждения')
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Заказ #{self.id} от {self.user.email} ({self.get_status_display()})"
    
    def calculate_total(self):
        """Рассчитывает общую сумму заказа на основе позиций"""
        total = sum(item.get_total() for item in self.items.all())
        self.total_amount = total
        return total
    
    def save(self, *args, **kwargs):
        """Пересчитывает общую сумму при сохранении"""
        if self.pk:
            self.calculate_total()
        super().save(*args, **kwargs)
    
    def can_be_cancelled(self):
        """Проверяет, можно ли отменить заказ"""
        return self.status in ['pending', 'confirmed', 'processing']
    
    def get_items_count(self):
        """Возвращает количество позиций в заказе"""
        return self.items.count()
    
    def get_stores_in_order(self):
        """Возвращает список магазинов, товары которых есть в заказе"""
        return Store.objects.filter(
            products__order_items__order=self
        ).distinct()


class OrderItem(models.Model):
    """Модель позиции заказа"""
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name='Товар'
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Цена за единицу'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'
        unique_together = ['order', 'product']
        indexes = [
            models.Index(fields=['order', 'product']),
        ]
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity} в заказе #{self.order.id}"
    
    def get_total(self):
        """Рассчитывает общую стоимость позиции"""
        return self.price * self.quantity
    
    def save(self, *args, **kwargs):
        """При сохранении позиции сохраняем цену товара на момент заказа"""
        if not self.pk:
            self.price = self.product.price
        super().save(*args, **kwargs)
        # Пересчитываем общую сумму заказа
        self.order.calculate_total()
        self.order.save()
