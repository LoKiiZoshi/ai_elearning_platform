from django.shortcuts import render

# Create your views here.
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Category, Course, Enrollment, Lesson, Module, Review
from .permissions import IsCourseOwnerOrReadOnly, IsInstructorOrReadOnly
from .serializers import(
    CategorySerializer,
    CourseDetailSerializer,
    CourseListSerializer,
    EnrollmentSerializer,
    LessonSerializer,
    moduleSerializer,
    ReviewSerializer,
    
)

class CategoryViewSet(viewsets.ModelViewSet):
    """/api/course/categories/ -- public read, admin write."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    search_fields = ["name","description"]
    ordering_fields = ["name","created_at"]
    
    def get_permissions(self):
        if self.action in ["create","update","partial_update","destory"]:
            return [permissions.AllowAny()]
        
class CourseViewSet(viewsets.ModelViewSet):
    """/api/courses/courses/
    -Public: list/retrieve published courses.
    -Instructors:full CRUD on their own courses.
    -Adminis: full Crud on everything."""
    
    permission_classes = [IsInstructorOrReadOnly, IsCourseOwnerOrReadOnly]
    lookup_field = "slug"
    filterset_fields = ["category","level","status","is_free","instructor"]
    search_fields = ["title","subtitle","description"]
    ordering_fields = ["created_at","price","average_rating","total_enrollments"]
    
    def get_queryset(self):
        qs = Course.objects.select_related("instructor","category").prefetch_related("modules__lessons","reviews")
        user = self.request.user
        if user.is_authenticated and (user.is_staff or user.is_admin_role):
            return qs
        if user.is_authenticated and user.is_instructor:
            return qs.filter(Q(status=Course.status.PUBLISHED) | Q(instructor = user))
        return qs.filter(status = Course.status.PUBLISHED)
    