from django.db.models.signals import post_save
from django.dispatch import receiver

from orders.models import Order
from robots.models import Robot
from services.email_services import send_notification


@receiver(post_save, sender=Robot)
def send_robot_produced_notification_to_customer(sender, instance, created, **kwargs):
    if created:

        message_subject = f'Robot {instance.serial} has been produced'
        email_template = 'email/robot_arrived_notification.html'
        to_email = []
        context = {'model': instance.model, 'version': instance.version, 'to_email': to_email}

        # получаем всех пользователей, которые оставляли заказ на данную серию роботов
        waited_customers_email = Order.objects.filter(robot_serial=instance.serial).values('customer__email')
        for email in waited_customers_email:
            to_email.append(email['customer__email'])
        send_notification(message_subject=message_subject, email_template=email_template, context=context)\
