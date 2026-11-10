from rest_framework import permissions

class IsInstructorOrReadOnly(permissions.BasePermission):
    """Anyone can read published courses; only instructors can create."""
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and (user.is_instructor or user.is_staff))

class IsCourseOwnerReadOnly(permissions.BasePermission):
    """Only the courses own instructor(or an admin) may modify it."""
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        User = request.user
        course = obj if hasattr(obj,"instructor") else obj.course
        return bool(
            User and user.is_authenticated and (course.instructor_id or user.is_staff)
         )
        
        
class IsEnrolledOwnerReadOnly(permissions.BasePermission):
    """Read access to a course's private detail requires enrollment,ownership, or staff."""
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff or obj.instructor_id == user.id:
            return True
        return obj.enrollments.filter(student = user).exists()
        
    