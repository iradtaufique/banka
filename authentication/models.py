from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model


class UserManager(BaseUserManager):

    def create_superuser(self, email, username, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            username=username,
            first_name='first_name',
            last_name='last_name',
        )
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user

    def create_user(self, email, username, first_name, last_name, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        if not username:
            raise ValueError('Users must have a username')

        if not first_name:
            raise ValueError('Users must have a first_name')

        if not last_name:
            raise ValueError('Users must have a last_name')
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email", max_length=30, unique=True)
    username = models.CharField(max_length=30, unique=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_super_user = models.BooleanField(default=False)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True)
    last_login = models.DateField(auto_now=True, verbose_name="Last login")
    date_joined = models.DateField(auto_now_add=True, verbose_name="Date joined")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

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

    @property
    def is_staff(self):
        """Is the user a member of staff?
         All admins are staff"""
        return self.is_admin

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh-token': str(refresh),
            'access-token': str(refresh.access_token)
        }

