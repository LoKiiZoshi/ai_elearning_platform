from django.db import models

from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy

class User(AbstractUser):
    
    """Custom user for the Ai E-Learning Platform.
    Authenticates via email instead of usename, and carries a role 
    that drives permissions across every other app (courses, learning ,certificates,ai_assistant, notifications)."""

    class Role(models.TextChoices):
        STUDENT = "student", _("student")
        INSTRUCTOR = "instructor",_("Instructor")
        ADMIN = "admin", _("Admin")
        
        
        id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
        email = models.EmailField(_("email address"), unique=True)
        role = models.CharField(max_length=20,choices=Role.choices,default= Role.STUDENT)
        is_verified = models.BooleanField(default=False,help_text="Whether the user has verified their email address.")
        
        date_of_birth = models.DateField(null=True,blank=True)
        phone_number = models.CharField(max_length=20,blank=True)
        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)
        
        USERNAME_FIELD = "email"
        REQUIRED_FIELDS = ["username"]
        
        
        class Meta:
            ordering = ["-created_at"]
            indexes = [
                models.Index(fields=["email"]),
                models.Index(fields=["role"]),
            ]
            
            
        def __str__(self):
            return f"{self.email}({self.get_role_display()})"
        
        @property
        def is_student(self):
            return self.role == self.Role.STUDENT
        
        @property
        def is_instructor(self):
            return self.role == self.Role.INSTRUCTOR
        
        @property
        def is_admin_role(self):
            return self.role == self.Role.ADMIN
    
 
class Profile(models.Model):
    """Extended, editable info about a user. Created automatically via signal/serializer."""
 
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
 
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", blank=True, null=True)
    bio = models.TextField(max_length=1000, blank=True)
    headline = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
 
    # Instructor-specific fields (harmless/blank for students)
    expertise = models.CharField(max_length=255, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ["-created_at"]
 
    def __str__(self):
        return f"Profile<{self.user.email}>"
 
 
class EmailOTP(models.Model):
    """One-time codes used for email verification and password reset."""
 
    class Purpose(models.TextChoices):
        VERIFY_EMAIL = "verify_email", _("Verify Email")
        RESET_PASSWORD = "reset_password", _("Reset Password")
 
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=Purpose.choices)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
 
    class Meta:
        ordering = ["-created_at"]
 
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
 
    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at
 
    def __str__(self):
        return f"OTP({self.purpose}) for {self.user.email}"
 