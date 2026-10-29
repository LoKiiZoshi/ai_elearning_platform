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