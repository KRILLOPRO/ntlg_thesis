# API Документация

## Базовый URL
```
http://localhost:8000/api/
```

## Аутентификация

Все запросы (кроме просмотра товаров) требуют токен аутентификации. Токен должен передаваться в заголовке:
```
Authorization: Token <your_token>
```

---

## 1. Авторизация и Регистрация

### Регистрация
**POST** `/api/auth/register/`

**Тело запроса:**
```json
{
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Иван",
    "last_name": "Иванов",
    "phone": "+79001234567"
}
```

**Ответ:**
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        "first_name": "Иван",
        "last_name": "Иванов",
        "phone": "+79001234567",
        "is_email_verified": false
    },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "message": "Пользователь успешно зарегистрирован. Email с подтверждением отправлен."
}
```

### Авторизация
**POST** `/api/auth/login/`

**Тело запроса:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Ответ:**
```json
{
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "username",
        ...
    },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
    "message": "Успешная авторизация"
}
```

### Профиль пользователя
**GET** `/api/auth/profile/` - Получить профиль  
**PATCH** `/api/auth/profile/` - Обновить профиль

---

## 2. Товары

### Список товаров
**GET** `/api/products/`

**Параметры запроса:**
- `store` - фильтр по магазину (ID)
- `search` - поиск по названию, описанию, артикулу
- `ordering` - сортировка (price, created_at, name)
- `page` - номер страницы

**Пример:**
```
GET /api/products/?store=1&search=ноутбук&ordering=-price
```

**Ответ:**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "store": {
                "id": 1,
                "name": "Магазин Электроники",
                ...
            },
            "name": "Ноутбук ASUS",
            "description": "Игровой ноутбук",
            "sku": "SKU-002",
            "price": "85000.00",
            "is_available": true,
            "stock_quantity": 8,
            "is_in_stock": true,
            ...
        }
    ]
}
```

### Детали товара
**GET** `/api/products/{id}/`

### Спецификация товара
**GET** `/api/products/{id}/specification/`

**Ответ включает дополнительную информацию:**
- Информацию о магазине
- Детальную информацию о наличии

---

## 3. Корзина

### Получить товары в корзине
**GET** `/api/cart/items/`

**Ответ:**
```json
{
    "order_id": 1,
    "total_amount": "100000.00",
    "items": [
        {
            "id": 1,
            "product": {...},
            "quantity": 2,
            "price": "50000.00",
            "total": "100000.00"
        }
    ]
}
```

### Добавить товар в корзину
**POST** `/api/cart/add/`

**Тело запроса:**
```json
{
    "product_id": 1,
    "quantity": 2
}
```

### Удалить товар из корзины
**DELETE** `/api/cart/remove/`

**Тело запроса:**
```json
{
    "item_id": 1
}
```

---

## 4. Адреса доставки

### Список адресов
**GET** `/api/delivery-addresses/`

### Создать адрес
**POST** `/api/delivery-addresses/`

**Тело запроса:**
```json
{
    "city": "Москва",
    "street": "Ленина",
    "house": "10",
    "apartment": "25",
    "postal_code": "123456",
    "is_default": true
}
```

### Обновить адрес
**PATCH** `/api/delivery-addresses/{id}/`

### Удалить адрес
**DELETE** `/api/delivery-addresses/{id}/`

---

## 5. Заказы

### Создать заказ (подтвердить корзину)
**POST** `/api/orders/`

**Тело запроса:**
```json
{
    "delivery_address_id": 1,
    "notes": "Дополнительные пожелания"
}
```

**Примечание:** Заказ создается из текущей корзины пользователя. После создания заказа отправляется email с подтверждением.

**Ответ:**
```json
{
    "id": 1,
    "user": 1,
    "delivery_address": {...},
    "status": "confirmed",
    "status_display": "Подтвержден",
    "total_amount": "100000.00",
    "items": [...],
    "items_count": 2,
    "created_at": "2024-01-01T12:00:00Z",
    "confirmed_at": "2024-01-01T12:00:05Z"
}
```

### Список заказов пользователя
**GET** `/api/orders/my_orders/`

### Детали заказа
**GET** `/api/orders/{id}/`

### Обновить статус заказа
**PATCH** `/api/orders/{id}/update_status/`

**Тело запроса:**
```json
{
    "status": "shipped"
}
```

**Доступные статусы:**
- `pending` - Ожидает подтверждения
- `confirmed` - Подтвержден
- `processing` - В обработке
- `shipped` - Отправлен
- `delivered` - Доставлен
- `cancelled` - Отменен

---

## Примеры использования

### Полный цикл работы с заказом

1. **Регистрация:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user",
    "password": "password123",
    "password_confirm": "password123"
  }'
```

2. **Авторизация:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

3. **Просмотр товаров:**
```bash
curl http://localhost:8000/api/products/
```

4. **Добавление товара в корзину:**
```bash
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

5. **Добавление адреса доставки:**
```bash
curl -X POST http://localhost:8000/api/delivery-addresses/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Москва",
    "street": "Ленина",
    "house": "10",
    "apartment": "25",
    "is_default": true
  }'
```

6. **Подтверждение заказа:**
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_address_id": 1
  }'
```

7. **Просмотр заказов:**
```bash
curl http://localhost:8000/api/orders/my_orders/ \
  -H "Authorization: Token <your_token>"
```

---

## Обработка ошибок

Все ошибки возвращаются в формате:
```json
{
    "error": "Описание ошибки"
}
```

Или для ошибок валидации:
```json
{
    "field_name": ["Сообщение об ошибке"]
}
```

**Коды статусов:**
- `200` - Успешно
- `201` - Создано
- `400` - Ошибка валидации
- `401` - Не авторизован
- `403` - Доступ запрещен
- `404` - Не найдено
- `500` - Ошибка сервера

