"""
Celery задачи для отправки email
"""
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Order


@shared_task
def send_registration_email(user_email, username):
    """Отправка email с подтверждением регистрации"""
    subject = 'Добро пожаловать в систему автоматизации закупок!'
    
    html_message = f"""
    <html>
    <body>
        <h2>Добро пожаловать, {username}!</h2>
        <p>Вы успешно зарегистрировались в системе автоматизации закупок.</p>
        <p>Ваш email: {user_email}</p>
        <p>Теперь вы можете начать делать заказы!</p>
        <br>
        <p>С уважением,<br>Команда системы закупок</p>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return f"Email отправлен на {user_email}"
    except Exception as e:
        return f"Ошибка при отправке email: {str(e)}"


@shared_task
def send_order_confirmation_email(order_id):
    """Отправка email с подтверждением заказа"""
    try:
        order = Order.objects.select_related('user', 'delivery_address').prefetch_related('items__product').get(id=order_id)
    except Order.DoesNotExist:
        return f"Заказ {order_id} не найден"
    
    user = order.user
    delivery_address = order.delivery_address
    
    subject = f'Подтверждение заказа #{order.id}'
    
    # Формируем список товаров
    items_list = []
    for item in order.items.all():
        items_list.append({
            'name': item.product.name,
            'quantity': item.quantity,
            'price': item.price,
            'total': item.get_total()
        })
    
    html_message = f"""
    <html>
    <body>
        <h2>Ваш заказ подтвержден!</h2>
        <p>Здравствуйте, {user.get_full_name() or user.username}!</p>
        <p>Ваш заказ #{order.id} успешно подтвержден.</p>
        
        <h3>Детали заказа:</h3>
        <p><strong>Статус:</strong> {order.get_status_display()}</p>
        <p><strong>Общая сумма:</strong> {order.total_amount} руб.</p>
        <p><strong>Дата создания:</strong> {order.created_at.strftime('%d.%m.%Y %H:%M')}</p>
        
        <h3>Товары:</h3>
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
            <tr>
                <th>Товар</th>
                <th>Количество</th>
                <th>Цена</th>
                <th>Итого</th>
            </tr>
    """
    
    for item in items_list:
        html_message += f"""
            <tr>
                <td>{item['name']}</td>
                <td>{item['quantity']}</td>
                <td>{item['price']} руб.</td>
                <td>{item['total']} руб.</td>
            </tr>
        """
    
    html_message += """
        </table>
    """
    
    if delivery_address:
        html_message += f"""
        <h3>Адрес доставки:</h3>
        <p>{delivery_address.get_full_address()}</p>
        """
    
    html_message += """
        <br>
        <p>Спасибо за ваш заказ!</p>
        <p>С уважением,<br>Команда системы закупок</p>
    </body>
    </html>
    """
    
    plain_message = strip_tags(html_message)
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return f"Email подтверждения заказа отправлен на {user.email}"
    except Exception as e:
        return f"Ошибка при отправке email: {str(e)}"
