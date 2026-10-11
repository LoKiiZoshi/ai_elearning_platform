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
        
