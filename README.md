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

## Структура проекта

```
ntlg_thesis/
├── procurement/          # Основной проект Django
│   ├── settings.py      # Настройки проекта
│   ├── urls.py          # Главный URL конфигуратор
│   ├── celery.py        # Конфигурация Celery
│   └── ...
├── users/               # Приложение пользователей
├── products/            # Приложение товаров
├── orders/              # Приложение заказов
├── stores/              # Приложение магазинов
├── requirements.txt     # Зависимости проекта
└── README.md           # Документация
```

## Этапы разработки

### Этап 1: Создание и настройка проекта ✅
- Создан Django-проект
- Настроена база данных PostgreSQL
- Настроен Celery для асинхронных задач
- Настроен Django REST Framework

### Этап 2: Проработка моделей данных (в процессе)
- Создание моделей для пользователей, товаров, заказов, магазинов

### Этап 3: Реализация импорта товаров (в процессе)
- Функции загрузки товаров из файлов

### Этап 4: Реализация APIViews (в процессе)
- API endpoints для всех основных операций

### Этап 5: Полностью готовый backend (в процессе)
- Полная интеграция и тестирование

## API Endpoints

API endpoints будут документированы после реализации Этапа 4.

## Лицензия

Проект создан в рамках учебной работы.

