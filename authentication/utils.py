"""this file is for sending emails"""
from django.core.mail import EmailMessage
from django.db import connection


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        email.send()

    def db_table_exists(table_name):
        return table_name in connection.introspection.table_names()