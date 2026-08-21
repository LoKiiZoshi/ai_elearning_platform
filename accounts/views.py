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
        
        
class CustomTokenObtainPairView(TokenObtainPairView):
    """POST/api/accounts/login/----email + password -> access/refresh tokens."""
    Serializer_class = CustomTokenObtainPairSerializer
    permissions_classes = [permissions.AllowAny]
    
class MeView(generics.RetrieveAPIView):
    """GET/PATCH/accounts/me -- the authenticated user's own record."""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.GenericAPIView):
    """POST /api/accounts/change-password/"""
 
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
 
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)
    
    
    
    

def _issue_and_send_otp(user, purpose):
    code = f"{random.randint(0, 999999):06d}"
    EmailOTP.objects.create(
        user=user,
        code=code,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    subject = {
        EmailOTP.Purpose.VERIFY_EMAIL: "Verify your email",
        EmailOTP.Purpose.RESET_PASSWORD: "Reset your password",
    }[purpose]
    send_mail(
        subject=subject,
        message=f"Your verification code is: {code}\nIt expires in 10 minutes.",
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
        recipient_list=[user.email],
        fail_silently=True,
    )   


class RequestOTPView(APIView):
    """POST /api/accounts/otp/request/ -- {email, purpose}"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args,**kwargs):
        serializer = RequestOTPSerializer(data = request.data)
        serializer.is_valid(raise_exception =True)
        User = User.objects.get(email = serializer.validated_data["email"])
        _issue_and_send_otp(User,serializer.validated_data("purpose"))
        return Response({"detail": "OTP sent."}, status=status.HTTP_200_OK)
    
    
class VerifyOTP(APIView):
    """POST /api/accounts/otp/verify/ -- {email, code , purpose, new_password}"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request,*args,**kwargs):
        serializer = VerifyOTPSerializer(data = request.data)
        serializer.is_valid(raise_exception = True)
        User = serializer.save()
        return Response(
    {"detail":"Verification successful.", "User": UserSerializer(User).data},
    status = status.HTTP_200_OK,)
        