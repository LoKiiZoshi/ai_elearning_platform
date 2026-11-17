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
    
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name","slug","parent","created_at")
    search_fields = ("name",)
    prepopulated_fields = {"slug":("name",)}
    
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = (
        "title", "instructor","category","level","status",
        "price","is_free","average_rating","total_enrollments","created_at",
        
    )
    list_filter = ("status","level","is_free","category")
    search_fields = ("title","instructor__email","description")
    prepopulated_fields = {"slug":("title",)}
    readonly_fields = ("average_rating","total_enrollments","created_at","updated_at")
    inlines = [ModuleInline]
    autocomplete_fields = ["instructor","category"]
    
    