from django.db import models
from django.core.validators import MinLengthValidator


class Store(models.Model):
    """Модель магазина"""
    name = models.CharField(max_length=200, verbose_name='Название магазина', unique=True)
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    address = models.CharField(max_length=500, blank=True, null=True, verbose_name='Адрес')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    
    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_active_products_count(self):
        """Возвращает количество активных товаров в магазине"""
        return self.products.filter(is_available=True).count()
