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
         
         
class LessonPreviewSerializer(serializers.ModelSerializer):
    """Used for non-enrolled students: hides content unless is_preview=True."""
    video_url = serializers.SerializerMetaclass()
    text_content = serializers.SerializerMethodField()
     
    class meta:
        model = Lesson
        fields = [
            "id","module","title","content_type","video_url","text_content",
            "duration_minutes","order","is_preview",
        ]
        
        def get_video_url(self,obj):
            return obj.video_url if obj.is_preview else None
        
        def get_text_content(self,obj):
            return obj.text_content if obj.is_preview else None
                
class moduleSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = ["id", "course", "title", "description","order","lessons","created_at"]
        read_only_fields = ["id","created_at"]
        
    def get_lessons(self, obj):
        request = self.context.get("request")
        enrolled = self.context.get("is_enrolled", False)
        if request and (enrolled or (request.user.is_authenticated and (
            request.user.is_staff or obj.course.instructor_id == request.user.id
        ))):
            return LessonSerializer(obj.lessons.all(), many=True, context=self.context).data
        return LessonPreviewSerializer(obj.lessons.all(), many=True, context=self.context).data
    def validate(self, attrs):
        course = attrs.get("course") or getattr(self.instance, "course", None)
        request = self.context.get("request")
        if course and request and not request.user.is_staff:
            if course.instructor_id != request.user.id:
                raise serializers.ValidationError("You do not own this course.")
            return attrs
    
 