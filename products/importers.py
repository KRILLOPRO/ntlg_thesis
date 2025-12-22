"""
Модуль для импорта товаров в базу данных
"""
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Tuple
from django.db import transaction
from stores.models import Store
from products.models import Product


class ProductImporter:
    """Класс для импорта товаров в базу данных"""
    
    REQUIRED_FIELDS = ['store_name', 'name', 'price']
    
    def __init__(self, dry_run: bool = False, verbose: bool = True):
        """
        Args:
            dry_run: Если True, не сохраняет данные в БД, только валидирует
            verbose: Если True, выводит подробную информацию
        """
        self.dry_run = dry_run
        self.verbose = verbose
        self.stats = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': []
        }
    
    def validate_row(self, row_data: Dict, row_number: int) -> Tuple[bool, List[str]]:
        """
        Валидирует строку данных
        
        Returns:
            Tuple[bool, List[str]]: (валидна ли строка, список ошибок)
        """
        errors = []
        
        # Проверка обязательных полей
        for field in self.REQUIRED_FIELDS:
            if not row_data.get(field) or str(row_data.get(field)).strip() == '':
                errors.append(f"Отсутствует обязательное поле: {field}")
        
        # Валидация цены
        if 'price' in row_data and row_data['price']:
            try:
                price = Decimal(str(row_data['price']).replace(',', '.'))
                if price <= 0:
                    errors.append("Цена должна быть больше нуля")
            except (InvalidOperation, ValueError):
                errors.append(f"Некорректное значение цены: {row_data['price']}")
        
        # Валидация количества на складе
        if 'stock_quantity' in row_data and row_data['stock_quantity']:
            try:
                quantity = int(row_data['stock_quantity'])
                if quantity < 0:
                    errors.append("Количество на складе не может быть отрицательным")
            except (ValueError, TypeError):
                errors.append(f"Некорректное значение количества: {row_data['stock_quantity']}")
        
        # Валидация is_available
        if 'is_available' in row_data and row_data['is_available']:
            is_available_str = str(row_data['is_available']).lower().strip()
            if is_available_str not in ['true', 'false', '1', '0', 'yes', 'no', 'да', 'нет', '']:
                errors.append(f"Некорректное значение доступности: {row_data['is_available']}")
        
        return len(errors) == 0, errors
    
    def normalize_data(self, row_data: Dict) -> Dict:
        """Нормализует данные строки"""
        normalized = {}
        
        # Название магазина
        normalized['store_name'] = str(row_data.get('store_name', '')).strip()
        
        # Название товара
        normalized['name'] = str(row_data.get('name', '')).strip()
        
        # Описание
        normalized['description'] = str(row_data.get('description', '')).strip() or None
        
        # Артикул
        normalized['sku'] = str(row_data.get('sku', '')).strip() or None
        
        # Цена
        price_str = str(row_data.get('price', '0')).replace(',', '.').strip()
        try:
            normalized['price'] = Decimal(price_str)
        except (InvalidOperation, ValueError):
            normalized['price'] = Decimal('0.00')
        
        # Количество на складе
        stock_str = str(row_data.get('stock_quantity', '0')).strip()
        try:
            normalized['stock_quantity'] = int(stock_str) if stock_str else 0
        except (ValueError, TypeError):
            normalized['stock_quantity'] = 0
        
        # Доступность
        is_available_str = str(row_data.get('is_available', 'true')).lower().strip()
        if is_available_str in ['true', '1', 'yes', 'да']:
            normalized['is_available'] = True
        elif is_available_str in ['false', '0', 'no', 'нет']:
            normalized['is_available'] = False
        else:
            normalized['is_available'] = True  # По умолчанию доступен
        
        return normalized
    
    def get_or_create_store(self, store_name: str) -> Store:
        """Получает или создает магазин"""
        store, created = Store.objects.get_or_create(
            name=store_name,
            defaults={'is_active': True}
        )
        if created and self.verbose:
            print(f"  Создан магазин: {store_name}")
        return store
    
    def import_product(self, row_data: Dict, row_number: int) -> Tuple[bool, str]:
        """
        Импортирует один товар
        
        Returns:
            Tuple[bool, str]: (успешно ли импортирован, сообщение)
        """
        # Валидация
        is_valid, errors = self.validate_row(row_data, row_number)
        if not is_valid:
            error_msg = f"Строка {row_number}: {', '.join(errors)}"
            self.stats['errors'].append(error_msg)
            self.stats['skipped'] += 1
            return False, error_msg
        
        # Нормализация данных
        normalized = self.normalize_data(row_data)
        
        # Получение или создание магазина
        store = self.get_or_create_store(normalized['store_name'])
        
        if self.dry_run:
            self.stats['processed'] += 1
            return True, f"Строка {row_number}: будет создан/обновлен товар '{normalized['name']}'"
        
        # Создание или обновление товара
        try:
            # Ищем товар по SKU или по названию и магазину
            product = None
            if normalized['sku']:
                product = Product.objects.filter(
                    store=store,
                    sku=normalized['sku']
                ).first()
            
            if not product:
                product = Product.objects.filter(
                    store=store,
                    name=normalized['name']
                ).first()
            
            if product:
                # Обновляем существующий товар
                product.name = normalized['name']
                product.description = normalized['description']
                product.price = normalized['price']
                product.stock_quantity = normalized['stock_quantity']
                product.is_available = normalized['is_available']
                if normalized['sku']:
                    product.sku = normalized['sku']
                product.save()
                self.stats['updated'] += 1
                action = "обновлен"
            else:
                # Создаем новый товар
                product = Product.objects.create(
                    store=store,
                    name=normalized['name'],
                    description=normalized['description'],
                    sku=normalized['sku'],
                    price=normalized['price'],
                    stock_quantity=normalized['stock_quantity'],
                    is_available=normalized['is_available']
                )
                self.stats['created'] += 1
                action = "создан"
            
            self.stats['processed'] += 1
            return True, f"Строка {row_number}: товар '{normalized['name']}' {action}"
            
        except Exception as e:
            error_msg = f"Строка {row_number}: ошибка при сохранении - {str(e)}"
            self.stats['errors'].append(error_msg)
            self.stats['skipped'] += 1
            return False, error_msg
    
    def import_from_parsed_data(self, parsed_data: List[Dict]) -> Dict:
        """
        Импортирует товары из распарсенных данных
        
        Args:
            parsed_data: Список словарей с данными о товарах (из парсера)
        
        Returns:
            Dict: Статистика импорта
        """
        if self.verbose:
            print(f"\nНачало импорта товаров (dry_run={self.dry_run})...")
            print(f"Найдено строк для обработки: {len(parsed_data)}\n")
        
        # Используем транзакцию только если не dry_run
        if not self.dry_run:
            with transaction.atomic():
                self._process_items(parsed_data)
        else:
            self._process_items(parsed_data)
        
        if self.verbose:
            print(f"\n{'='*50}")
            print("Статистика импорта:")
            print(f"  Обработано: {self.stats['processed']}")
            print(f"  Создано: {self.stats['created']}")
            print(f"  Обновлено: {self.stats['updated']}")
            print(f"  Пропущено: {self.stats['skipped']}")
            print(f"  Ошибок: {len(self.stats['errors'])}")
            print(f"{'='*50}\n")
        
        return self.stats
    
    def _process_items(self, parsed_data: List[Dict]):
        """Внутренний метод для обработки элементов"""
        for item in parsed_data:
            row_number = item['row_number']
            row_data = item['data']
            
            success, message = self.import_product(row_data, row_number)
            
            if self.verbose:
                if success:
                    print(f"✓ {message}")
                else:
                    print(f"✗ {message}")

