from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_siplejwt.serializers import TokenObtainSerializer
from .models import EmailOTP, Profile

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "avatar",
            "bio",
            "headline",
            "country",
            "website",
            "linkedin_url",
            "twitter_url",
            "expertise",
            "years_of_experience",
            "created_at",
            "updated_at",
        ]
        
        read_only_fields = ["id","created_at","updated_at"]
        
        
class UserSerializer(serializers.ModelSerializer):
    """Read-mostly representation of a user, including their profile."""
    Profile = ProfileSerializer(read_only = True)
    
    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "is_verified",
            "phone_number",
            "date_of_birth",
            "profile",
            "date_joined",
            "created_at",
        ]
        
        read_only_fields = ["id","role","is_verified","date_joined","created_at"]
        
        
class UserAdminSerializer(UserSerializer):
    """Adds admin -only writable fields (role, is_active)."""
    
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["is_active"]
        read_only_fields = ["id","date_joined","created_at"]
        
        
class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only =True,required =True)
    password2 = serializers.CharField(write_only = True, required = True)
    
    
    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "password",
            "password2",
        ]
        
        extra_kwargs = {
            "role": {"required": False}
        }
        
        
        def validate_role(self, value):
            # Prevent self-registration as admin.
            if value == User.Role.ADMIN:
                raise serializers.ValidationError("You cannot self-register as an admin.")
            return value
        
        def validate(self, attrs):
            if attrs["password"] != attrs.pop("password2"):
                raise serializers.ValidationError({"password2":"Password do not match."})
            self.validate_password(attrs["password"])
            return attrs
        
        def create(self, validated_data):
            password = validated_data.pop("password")
            user = User(**validated_data)
            user.set_password(password)
            user.save()
            Profile.objects.get_or_create(user=User)
            return User
        
class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    """JWT serializer that logs in via email and embeds role/verification claims."""  
    
    username_fields = User.USERNAME_FIELD
    
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token("role") = user.role
        token["is_verified"] = user.is_verified
        return token
    
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
    
class ChnagePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(required = True,write_only = True)
    new_password = serializers.CharField(required = True,write_only =True)
    new_password2 = serializers.CharField(required = True, write_only = True)
    
    def validate_old_password(self, value):
        user = self.context["request"].user
        if not User.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    def validate(self, attrs):
        if attrs["new_password"] ! = attrs["new_password2"]:
            raise serializers.ValidationError({"new_password2": "Password do not match."})
        
        validate_password(attrs["new_password"])
        return attrs
    
    def save(self, **kwargs):
        User = self.context["request"].user
        User.set_password(self.validated_data["new_password"])
        User.save()
        return User
    
class RequestOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    purpose = serializers.ChoiceField(choices=EmailOTP.Purpose.choices)
    
    def validate_email(self, value):
        if not User.objects.filter(email = value).exists():
            raise serializers.ValidationError("No account found with this email.")
        return value
    
    
class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length = 6)
    purpose = serializers.ChoiceField(choices=EmailOTP.Purpose.choices)
    new_password = serializers.ChoiceField(required = False,write_only = True)
    
    def validate(self, attrs):
        try:
            User = User.objects.get(email=attrs["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email":"No account found with this email."})
        otp = (
            EmailOTP.objects.filter(
                User = User, code = attrs["code"], purpose = attrs["purpose"], is_used = False
            ).order_by("-created_at")
        )