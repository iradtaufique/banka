from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


class CustomUserManager(BaseUserManager):
    def create_superuser(self, email, full_name, password=None,  **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        other_fields.setdefault('is_admin', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                'Superuser must be assigned to is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                'Superuser must be assigned to is_superuser=True.')

        return self.create_user(email, full_name, password,  **other_fields)

    def create_user(self, email, full_name, password, **other_fields):

        if not email:
            raise ValueError('You must provide an email address')

        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **other_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name='Email Address', unique=True)
    full_name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=12, blank=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """Does the user have a specific permission?
        Yes, always"""
        return True

    def has_module_perms(self, app_label):
        """Does the user have permissions to view the app `app_label`?
        Yes, always"""
        return True


    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh-token': str(refresh),
            'access-token': str(refresh.access_token)
        }