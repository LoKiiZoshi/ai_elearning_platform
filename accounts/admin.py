from django.contrib import admin

# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import EmailOTP, Profile, User

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"
    
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    
    list_display = (
        "email",
        "username",
        "role",
        "is_verified",
        "is_active",
        "is_staff",
        "created_at",
    )
    list_filter = ("role","is_verified","is_active","is_staff")
    search_fields = ("email","username","first_name","last_name")
    ordering = ("-created_at",)
    readonly_fields = ("id","created_at","updated_at","last_login","date_joined")
    fieldsets = (
        (None,{"fields":("id","email","username","password")}),
        ("Personal info",{"fields":("first_name","last_name","phone_number","date_of_birth")}),
        ("Role & Status", {"fields": ("role","is_verified","is_active","is_staff","is_superuser")}),
        ("permissions",{"fields":("groups","user_permissions")}),
        ("Important dates",{"fields":("last_login","date_joined","created_at","updated_at")}),
        
    )
    add_fieldsets = (
        None,
        {
            "classes":("wide",),
            "fields":("email","username","role","password1","password2",)
        },
    ),
    
    
