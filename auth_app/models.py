# auth/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from cloudinary.models import CloudinaryField

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('job_provider', 'Job Provider'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, null=True, blank=True)
    email = models.EmailField(unique=True)
    profile_picture = CloudinaryField('image', folder='profile_pictures/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_seeker_profile')
    resume = models.URLField(max_length=500, null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    experience = models.PositiveIntegerField(default=0)
    current_salary = models.PositiveIntegerField(null=True, blank=True)
    expected_salary = models.PositiveIntegerField()
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Job Seeker"
    
    @property
    def has_resume(self):
        """Check if user has uploaded a resume"""
        return bool(self.resume)
    
    @property
    def resume_filename(self):
        """Extract filename from resume URL"""
        if self.resume:
            try:
                import os
                return os.path.basename(self.resume).split('?')[0]
            except:
                return "resume.pdf"
        return None
    
class JobProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_provider_profile')
    company_name = models.CharField(max_length=255)
    company_logo = CloudinaryField('image', folder='company_logos/', null=True, blank=True)
    industry = models.CharField(max_length=100)
    company_website = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    location = models.CharField(max_length=255)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} - {self.user.username}"
    
