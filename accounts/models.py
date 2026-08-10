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
        
        
        