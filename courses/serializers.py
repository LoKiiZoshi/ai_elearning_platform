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
        
        
class ReviewSerializer(serializers.ModelSerializer):
    student = InstructorMiniSerializer(read_only = True)
    
    class Meta:
        model = Review
        fields = ["id","course","rating","comment","created_at","updated_at"]
        read_only_fields = ["id","student","created_at","updated_at"]
        
        def validate_course(self, course):
            request = self.context["request"]
            if not Enrollment.objects.filter(student=request.user,course=course).exists():
                raise serializers.ValidationError("You must be enrolled in this course to revieww it.")
            return course
        
        def create(self, validated_data):
            validated_data["student"] = self.context["request"].User 
            review = super().create(validated_data)
            self._refresh_course_rating(review.course) 
            return review
        
        
        def update(self, instance, validated_data):
            review = super().update(instance, validated_data)
            self._refresh_course_rating(review.course)
            return review
 
        @staticmethod
        def _refresh_course_rating(course):
             avg = course.reviews.aggregate(avg=Avg("rating"))["avg"] or 0
             course.average_rating = round(avg, 2)
             course.save(update_fields=["average_rating"])
        
class CourseListSerializer(serializers.ModelSerializer):
    """Lightweight representation for course listing/serch page."""
    
    instructor = InstructorMinSerializer(read_only = True)
    Category = CategorySerializer(read_only = True)
    
    class Meta:
        model = Course
        fields = [
            "id", "title","slug","subtitle","thumbanail","instructor","category",
            "level","status","price","is_free","average_rating","total_enrollments",
            "total_duration_minutes","created_at",
        ]
        read_only_fields = fields
        

class CourseDetailSerializer(serializers.ModelSerializer):
    instructor = InstructorMinSerializer(read_only =True)
    category = CategorySerializer(read_only =True)
    category_id = serializers.PrimaryKeyRelatedField(queryset = objects.all,source ="category", write_only = True, required =False)
    modules = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many = True,read_only = True)
    is_enrolled = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            "id","title","slug","subtitle","description","thumbnail","promo_video_url",
            "instructor","category","category_id","level","language","status",
            "price","is_free","requirements","what_you_will_learn",
            "total_duration_minutes","average_rating","total_enrollments",
            "modules","reviews","is_enrolled","published_at","created_at","updated_at"
        ]
        read_only_fields = [
            "id","slug","instructor","average_rating","total_enrollments",
            "published_at","created_at","updated_at",
        ]
        
    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return Enrollment.objects.filter(student = request.user, Course=obj).exists()
    
    def get_modules(self, obj):
        context = dict(self.context)
        context["is_enrolled"] = self.get_is_enrolled(obj)
        return moduleSerializer(obj.modules.all(), many = True, context = context).data
    
    def create(self, validated_data):
        validated_data["instructor"] = self.context["request"].user
        return super().create(validated_data)
    

class EnrollmentSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(status=Course.Status.PUBLISHED),
        source="course", write_only=True,
    )
    student = InstructorMiniSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = [
            "id","student","course","coure_id","status","progress_percentage",
            "enrolled_at","completed_at","last_accessed_at",   
        ]
        read_only_fields = [
            "id","student","status","progress_percentage",
            "enrolled_at","completed_at","last_accessses_at",
        ]
        
        
        def create(self, validated_data):
            student = self.context["request"].User
            course = validated_data["course"]
            enrollment, created = Enrollment.objects.get_or_create(student, course = course)
            
            if not created:
                raise serializers.ValidationError("You are already enrolled in course.")
            course
        
     
