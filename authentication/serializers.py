from rest_framework import serializers
from .models import User
from rest_framework.exceptions import AuthenticationFailed
from django.contrib import auth


"""serializer for registering user"""
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'first_name', 'last_name', 'password']

    """ method for validating inputs from user"""
    def validate(self, attrs):
        email = attrs.get('email', )
        username = attrs.get('username', )

        if not username.isalnum():
            raise serializers.ValidationError('The username should contain alphanumeric character')

        return attrs

    """method for creating user """
    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


"""Serializer for verifying email"""
class EmailVerificationSerializer(serializers.ModelField):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ['token']


"""serializer for loging user"""
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=69, min_length=4, write_only=True)
    username = serializers.CharField(max_length=255, min_length=3, read_only=True)
    tokens = serializers.CharField(max_length=69, min_length=6, read_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'username', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email', )
        password = attrs.get('password', )

        """authenticating user with their credetials"""
        user = auth.authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed('Invalid credentials')

        if not user.is_active:
            raise AuthenticationFailed('User Account is Disabled')

        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens,
        }

        return super().validate(attrs)
