from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import(
    ChangePasswordView,CustomTokenObtainPairView,
    MeView,
    ProfileViewSet,
    RegisterView,
    RequestOTPView,
    UserViewSet,
    VerifyOTPView,
)

app_name = "accounts"

router = DefaultRouter()
router.register(r"profiles",ProfileViewSet,basename="profile")
router.register(r"users",UserViewSet, basename="user")


urlpatterns = [
    #Auth
    path("register/", RegisterView.as_view(), name = "register"),
    path("login/", CustomTokenObtainPairView.as_view(),name="login"),
    path("login/refresh/",TokenRefreshView.as_view(),name = "login"),
    path("login/verify",TokenVerifyView.as_view(), name = "login-verify"),
    
    # Self - service
    path("me/", MeView.as_view(),name="me"),
    path("change-password/", ChangePasswordView.as_view(),name="change-password"),
    #Email verfication / password reset via OTP
    path("otp/request/", RequestOTPView.as_view(), name="otp-request"),
    path("otp/verify/",VerifyOTPView.as_view(), name="otp-verify"),
    # Router- backend CRUD: /profiles/,/users/
    path("", include(router.urls)),
    
]
