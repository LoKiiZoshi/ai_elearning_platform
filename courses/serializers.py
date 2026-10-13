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
        

class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        Model = Lesson
        fields = [
            "id","module","title","content_type","video_url","text_content",
            "resource_file","duration_minutes","order","is_preview",
            "created_at","updated_at",
        ]
        read_only_fields = ["id","created_at","updated_at"]
        
        def validate(self, attrs):
            Module = attrs.get("module") or getattr(self.instance,"module", None)
            request = self.context.get("request")
            if module and request and not request.user.is_staff:
             if module.course.request.instructor_id != request.user.id:
                 raise serializers.ValidationError("You do not own the course this module belongs to.")
             return attrs
                