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