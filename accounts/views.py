from django.shortcuts import render
# Create your views here.
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


from rest_framework import generics,permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import EmailOTP, Profile
from .permissions import IsAdminRole, IsOwnerOrAdmin
from .serializers import(
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    RegisterSerializer,
    RequestOTPSerializer,
    UserAdminSerializer,
    UserSerializer,
    VerifyOTPSerializer,
)


User = get_user_model()
class RegisterView(generics.CreateAPIView):
    """POST /api/account/register/---- open anyone"""
    
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permission.AllowAny]
    
    def create(self,request,*args, **kwargs):
        serializer = self.get_serializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        User = serializer.save()
        _issue_and_send_otp(User, EmailOTP.Purpose.VERIFY_EMAIL)
        return Response(
            {
                "user":  UserSerializer(User).data,
                "detail":"Registration successful. Check your email for a verification code."
            },
            status=status.HTTTP_201_CREATED,
        )