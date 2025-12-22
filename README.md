Backend приложение для автоматизации закупок, построенное на Django REST Framework.

## Технологии

- Python 3.10+
- Django 4.2.7
- PostgreSQL
- Celery 5.3.4
- Redis
- Django REST Framework

## Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd ntlg_thesis
```

### 2. Создание виртуального окружения

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Создайте файл `.env` на основе `.env.example`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите свои настройки:
- Настройки базы данных PostgreSQL
- Настройки Redis для Celery
- Настройки email для отправки писем

### 5. Настройка базы данных PostgreSQL

Убедитесь, что PostgreSQL установлен и запущен. Создайте базу данных:

```bash
createdb procurement_db
```

Или через psql:

```sql
CREATE DATABASE procurement_db;
```

### 6. Применение миграций

```bash
python manage.py migrate
```

### 7. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 8. Запуск Redis (для Celery)

```bash
redis-server
```

### 9. Запуск Celery Worker

В отдельном терминале:

```bash
celery -A procurement worker -l info
```

### 10. Запуск Celery Beat (если нужны периодические задачи)

В отдельном терминале:

```bash
celery -A procurement beat -l info
```

### 11. Запуск Django сервера разработки

```bash
python manage.py runserver
```

Сервер будет доступен по адресу: http://127.0.0.1:8000/

## Импорт товаров

Для импорта товаров из файлов используйте команду:

```bash
python manage.py import_products import_files/example_products.csv
```

Подробнее см. `import_files/README.md`

## API Документация

Полная документация по API доступна в файле `API_DOCUMENTATION.md`

## Тестовые сценарии

Примеры использования API и тестовые сценарии описаны в файле `test_scenarios.md`

## Структура проекта

```
ntlg_thesis/
├── procurement/          # Основной проект Django
│   ├── settings.py      # Настройки проекта
│   ├── urls.py          # Главный URL конфигуратор
│   ├── celery.py        # Конфигурация Celery
│   └── ...
├── users/               # Приложение пользователей
│   ├── models.py        # Модель User
│   ├── views.py         # API для авторизации и регистрации
│   └── serializers.py  # Сериализаторы
├── products/            # Приложение товаров
│   ├── models.py        # Модель Product
│   ├── views.py         # API для товаров
│   ├── serializers.py  # Сериализаторы
│   ├── parsers.py      # Парсинг файлов
│   └── importers.py    # Импорт товаров
├── orders/              # Приложение заказов
│   ├── models.py        # Модели Order, OrderItem, DeliveryAddress
│   ├── views.py         # API для заказов и корзины
│   ├── serializers.py  # Сериализаторы
│   └── tasks.py        # Celery задачи для email
├── stores/              # Приложение магазинов
│   ├── models.py        # Модель Store
│   └── serializers.py  # Сериализаторы
├── requirements.txt     # Зависимости проекта
└── README.md           # Документация
```

## Этапы разработки

### Этап 1: Создание и настройка проекта ✅
- Создан Django-проект
- Настроена база данных PostgreSQL
- Настроен Celery для асинхронных задач
- Настроен Django REST Framework

### Этап 2: Проработка моделей данных ✅
- Созданы модели для пользователей, товаров, заказов, магазинов
- Добавлены методы для работы с моделями
- Настроена админка Django

### Этап 3: Реализация импорта товаров ✅
- Функции загрузки товаров из CSV и Excel файлов
- Management команда для импорта
- Валидация и обработка ошибок

### Этап 4: Реализация APIViews ✅
- API endpoints для всех основных операций
- Авторизация и регистрация
- Работа с товарами, корзиной, заказами
- Отправка email через Celery

### Этап 5: Полностью готовый backend ✅
- Все API endpoints работают корректно
- Реализованы все требуемые сценарии
- Система готова к использованию

## Основные функции

- ✅ Регистрация и авторизация пользователей
- ✅ Просмотр каталога товаров
- ✅ Добавление товаров в корзину (от разных магазинов)
- ✅ Управление адресами доставки
- ✅ Создание и подтверждение заказов
- ✅ Просмотр истории заказов
- ✅ Отправка email уведомлений через Celery
- ✅ Импорт товаров из файлов

## Лицензия

Проект создан в рамках учебной работы.
