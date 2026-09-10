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
    
    
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "headline","country","years_of_experience","updated_at")
    search_fields = ("user_email","headline","country","expertise")
    list_filter = ("country",)



@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("user", "purpose","code","is_used","expires_at","created_at")
    list_filter = ("purpose","is_used")
    search_fields = ("user__email","code")
    readonly_fields = ("created_at",)
    
    
