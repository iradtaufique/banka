from .models import User
from .serializers import RegisterSerializer, EmailVerificationSerializer, LoginSerializer
from rest_framework import generics, status, views
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import Util
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import jwt
from django.conf import settings


"""APIView for registering user"""
class RegisterAPIView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        print('serializer')
        print(serializer.validated_data)
        serializer.save()
        user_data = serializer.data

        """get user email"""
        user = User.objects.get(email=user_data['email'])

        """create token"""
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain

        relativeLink = reverse('verify_email')
        absurl = 'http://' + current_site + relativeLink + "?token=" + str(token)

        email_body = 'Hi ' + user.username + ' Use the Link to verify your account \n' + absurl

        data = {
            'email_body': email_body, 'to_email': user.email, 'email_subject': 'Verify Your Email'
        }

        """send email"""
        Util.send_email(data)
        return Response(user_data, status=status.HTTP_201_CREATED)


"""view for verifying user"""
class VerifyEmail(views.APIView):
    serializer_class = EmailVerificationSerializer

    token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
            return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        # check if token expired
        except jwt.ExpiredSignatureError as identifier:
            return Response({'error': 'Activation Link Expired'}, status=status.HTTP_400_BAD_REQUEST)

        # check if token was edited before being used
        except jwt.exceptions.DecodeError as identifier:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


"""view for loging user"""
class LoginAPIView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)