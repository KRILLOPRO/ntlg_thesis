# Тестовые сценарии для проверки работы системы

## Сценарий 1: Регистрация и авторизация

### Шаг 1: Регистрация пользователя
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Тест",
    "last_name": "Пользователь"
  }'
```

**Ожидаемый результат:**
- Пользователь создан
- Получен токен авторизации
- Email с подтверждением отправлен (через Celery)

### Шаг 2: Авторизация
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**Ожидаемый результат:**
- Получен токен авторизации
- Получена информация о пользователе

---

## Сценарий 2: Просмотр товаров

### Шаг 1: Получить список товаров
```bash
curl http://localhost:8000/api/products/
```

**Ожидаемый результат:**
- Список доступных товаров
- Возможность фильтрации по магазину, поиска, сортировки

### Шаг 2: Получить детали товара
```bash
curl http://localhost:8000/api/products/1/
```

### Шаг 3: Получить спецификацию товара
```bash
curl http://localhost:8000/api/products/1/specification/
```

**Ожидаемый результат:**
- Детальная информация о товаре
- Информация о магазине
- Информация о наличии

---

## Сценарий 3: Работа с корзиной (товары от разных магазинов)

### Шаг 1: Добавить товар из первого магазина
```bash
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2
  }'
```

### Шаг 2: Добавить товар из второго магазина
```bash
curl -X POST http://localhost:8000/api/cart/add/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 5,
    "quantity": 1
  }'
```

**Ожидаемый результат:**
- Оба товара добавлены в корзину
- Корзина содержит товары от разных магазинов

### Шаг 3: Просмотр корзины
```bash
curl http://localhost:8000/api/cart/items/ \
  -H "Authorization: Token <your_token>"
```

**Ожидаемый результат:**
- Список всех товаров в корзине
- Общая сумма заказа
- Товары от разных магазинов отображаются корректно

### Шаг 4: Удаление товара из корзины
```bash
curl -X DELETE http://localhost:8000/api/cart/remove/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "item_id": 1
  }'
```

---

## Сценарий 4: Работа с адресами доставки

### Шаг 1: Добавить адрес доставки
```bash
curl -X POST http://localhost:8000/api/delivery-addresses/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Москва",
    "street": "Ленина",
    "house": "10",
    "apartment": "25",
    "postal_code": "123456",
    "is_default": true
  }'
```

**Ожидаемый результат:**
- Адрес создан
- Адрес установлен как адрес по умолчанию

### Шаг 2: Получить список адресов
```bash
curl http://localhost:8000/api/delivery-addresses/ \
  -H "Authorization: Token <your_token>"
```

### Шаг 3: Удалить адрес
```bash
curl -X DELETE http://localhost:8000/api/delivery-addresses/1/ \
  -H "Authorization: Token <your_token>"
```

---

## Сценарий 5: Подтверждение заказа

### Шаг 1: Подтвердить заказ
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Token <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "delivery_address_id": 1,
    "notes": "Позвонить перед доставкой"
  }'
```

**Ожидаемый результат:**
- Заказ создан со статусом "confirmed"
- Заказ содержит товары от разных магазинов
- Email с подтверждением отправлен (через Celery)
- Заказ содержит адрес доставки

---

## Сценарий 6: Просмотр заказов

### Шаг 1: Получить список заказов
```bash
curl http://localhost:8000/api/orders/my_orders/ \
  -H "Authorization: Token <your_token>"
```

**Ожидаемый результат:**
- Список всех заказов пользователя
- Заказы отсортированы по дате создания (новые первые)

### Шаг 2: Получить детали заказа
```bash
curl http://localhost:8000/api/orders/1/ \
  -H "Authorization: Token <your_token>"
```

**Ожидаемый результат:**
- Детальная информация о заказе
- Список всех товаров в заказе
- Информация об адресе доставки
- Статус заказа

### Шаг 3: Обновить статус заказа (для администратора)
```bash
curl -X PATCH http://localhost:8000/api/orders/1/update_status/ \
  -H "Authorization: Token <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "shipped"
  }'
```

---

## Полный цикл работы системы

1. ✅ Пользователь регистрируется → получает email с подтверждением
2. ✅ Пользователь авторизуется → получает токен
3. ✅ Пользователь просматривает товары (без авторизации)
4. ✅ Пользователь добавляет товары от разных магазинов в корзину
5. ✅ Пользователь добавляет адрес доставки
6. ✅ Пользователь подтверждает заказ → получает email с подтверждением
7. ✅ Пользователь просматривает список заказов
8. ✅ Пользователь открывает детали созданного заказа

---

## Проверка работы Celery

### Проверка отправки email при регистрации:
1. Зарегистрировать нового пользователя
2. Проверить логи Celery worker
3. Проверить почтовый ящик (если настроен)

### Проверка отправки email при подтверждении заказа:
1. Создать заказ
2. Проверить логи Celery worker
3. Проверить почтовый ящик

---

## Примечания

- Все запросы к API (кроме просмотра товаров) требуют токен авторизации
- Токен передается в заголовке: `Authorization: Token <your_token>`
- Email отправляется асинхронно через Celery
- Для работы Celery нужно запустить worker: `celery -A procurement worker -l info`
- Для работы с email нужно настроить SMTP в `.env` файле

