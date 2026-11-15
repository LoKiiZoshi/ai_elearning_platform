from django.contrib import admin

# Register your models here.

from .models import Category,Course,Enrollment,Lesson,Module,Review

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ("title","content_type","order","duration_minutes","is_preview")
    
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    fields = ("title","order")
    show_change_link = True