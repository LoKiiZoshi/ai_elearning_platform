from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework import serializers

from .models import Category, Course, Enrollment, Lesson, Module, Review

User = get_user_model()

class InstructorMinSerializer(serializers.ModelSerializer):
    """Lightweight instructor info to embed in course responses."""
    
    class Meta:
        model = User
        fields = ["id","Username","first_name","last_name","email"]
        read_only_fields = fields
        
class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.IntegerField(source="courses.count", read_only=True)
 
    class Meta:
        model = Category
        fields = [
            "id", "name", "slug", "description", "icon", "parent", "course_count", "created_at",
        ]
        read_only_fields = ["id", "slug", "created_at"]