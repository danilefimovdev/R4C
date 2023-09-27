from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from R4C import settings


def send_notification(message_subject: str, email_template: str, context: dict):

    from_email = settings.DEFAULT_FROM_EMAIL
    message = render_to_string(email_template, context)
    to_email = context['to_email']
    mail = EmailMessage(message_subject, message, to=to_email, from_email=from_email)
    mail.send()
