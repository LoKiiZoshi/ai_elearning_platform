from django.conf import settings
from rest_framework import permissions

class IsAdminRole(permissions.BasePermission):
    """Allow access only to users with role = admin or django staff/superusers."""
    
    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_admin_role or user.is_staff or user.is_superuser)
        )
        
        
class IsOwnerOrAdmin(permissions.BasePermission):
    """Object-level permisson: owner of the record, or an admin, may acess it."""
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        owner = getattr(obj,"user",obj)
        return bool(
            user
            and user.is_authenticated
            and (owner == user or user.is_admin_role or user.is_staff or user.is_superuser)
        )        
        