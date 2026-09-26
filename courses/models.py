from django.db import models
import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator , MinValueValidator
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _ 


User = settings.AUTH_USER_MODEL

class Category(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=170,unique=True,blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True, help_text="Icon name/class for the frontend.")
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True,blank=True,related_name="subcategories")
    careated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            super().save(*args,**kwargs)
            
    def __str__(self):
        return self.name
    
    


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "beginner", _("Beginner")
        INTERMEDIATE = "intermediate",_("Intermediate")
        ADVANCED = "advanced", _("Advanced")
        ALL_LEVELS = "all_levels",_("All Levels")
        
        
    class Status(models.TextChoices):
        DRAFT = "draft",_("Draft")
        PENDING_REVIEW = "pending_review",_("Pending Review")
        PUBLISHED = "published",_("Published")
        ARCHIVED = "archived",_("Archived")
        
        
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="courses_taught",
        limit_choices_to={"role": "instructor"},
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="courses"
    )
 
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    subtitle = models.CharField(max_length=255, blank=True)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to="course_thumbnails/%Y/%m/", blank=True, null=True)
    promo_video_url = models.URLField(blank=True)
 
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.ALL_LEVELS)
    language = models.CharField(max_length=50, default="English")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
 
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    is_free = models.BooleanField(default=False)
 
    requirements = models.TextField(blank=True, help_text="One requirement per line.")
    what_you_will_learn = models.TextField(blank=True, help_text="One learning outcome per line.")
 
    total_duration_minutes = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_enrollments = models.PositiveIntegerField(default=0)
 
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["slug"]),
        ]
 
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Course.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
 
    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED
 
    def __str__(self):
        return self.title

    
class Module(models.Model):
    """A section/chapter within a course, conting ordered lessons."""
    
    course = models.ForeignKey(Course, on_delete=models.CASCADE,related_name="modules")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    class Meta:
        ordering = ["order","created_at"]
        unique_together = ["course","order"]
        
    def __str__(self):
        return f"{self.course.title} - Module {self.order}: {self.title}"
    

    
    


