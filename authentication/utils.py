"""this file is for sending emails"""
from django.core.mail import EmailMessage
from django.db import connection

from wallet.models import Notification


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()

    def db_table_exists(table_name):
        return table_name in connection.introspection.table_names()

    def save_notification(user, amount, content, transaction_from, ):
        Notification(user=user, transaction_from=transaction_from, received_amount=amount, content=content, sent=False).save()