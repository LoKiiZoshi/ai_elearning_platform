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
    
    
    


