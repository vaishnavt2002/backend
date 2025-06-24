import email
from rest_framework import serializers
from .models import User, JobProvider, JobSeeker
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import random
from django.core.validators import RegexValidator

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'user_type', 'profile_picture', 'phone_number', 'is_verified', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']





class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_type = serializers.ChoiceField(choices=User.USER_TYPE_CHOICES)
    company_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    company_website = serializers.URLField(required=False, allow_blank=True, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    company_logo = serializers.ImageField(required=False, allow_null=True)
    industry = serializers.CharField(max_length=100, required=False, allow_blank=True)
    location = serializers.CharField(max_length=255, required=False, allow_blank=True)
    phone_number = serializers.CharField(
        validators=[RegexValidator(regex=r'^[4-9]\d{9}$', message='Phone number must be 10 digits and start with a digit between 4-9')])
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = [
            'email', 'password', 'user_type', 'phone_number',
            'company_name', 'company_website', 'description', 'company_logo', 'industry', 'location'
        ]

    def validate_password(self, value):
        errors = []
        if len(value) < 6:
            errors.append("Password must be at least 6 characters long.")
        if not any(c.isupper() for c in value):
            errors.append("Password must contain at least one uppercase letter.")
        if not any(c.islower() for c in value):
            errors.append("Password must contain at least one lowercase letter.")
        if not any(c.isdigit() for c in value):
            errors.append("Password must contain at least one number.")
        if errors:
            raise serializers.ValidationError(errors)
        return value

    def validate(self, data):
        user_type = data.get('user_type')

        if user_type == 'job_provider':
            if not data.get('company_name'):
                raise serializers.ValidationError({"company_name": "This field is required for Job Providers."})
            if len(data.get('company_name', '')) < 4:
                raise serializers.ValidationError({"company_name": "Company name must be at least 4 characters long."})
            if not data.get('company_name', '').strip()[0].isalnum():
                raise serializers.ValidationError({"company_name": "Company name must not start with a special character."})

            if not data.get('industry'):
                raise serializers.ValidationError({"industry": "This field is required for Job Providers."})

            if not data.get('location'):
                raise serializers.ValidationError({"location": "This field is required for Job Providers."})
            if not data.get('location', '').strip() or not all(
                c.isalnum() or c in ' ,-.' for c in data.get('location', '')
            ):
                raise serializers.ValidationError({
                    "location": "Location can only contain letters, numbers, spaces, commas, hyphens, and periods."
                })

            if data.get('company_logo'):
                valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
                extension = data.get('company_logo').name.split('.')[-1].lower()
                if extension not in valid_extensions:
                    raise serializers.ValidationError({
                        "company_logo": "Company logo must be in JPG, JPEG, PNG, or GIF format."
                    })

        return data

    def create(self, validated_data):
        job_provider_data = {
            'company_name': validated_data.pop('company_name', None),
            'company_website': validated_data.pop('company_website', None),
            'description': validated_data.pop('description', None),
            'company_logo': validated_data.pop('company_logo', None),
            'industry': validated_data.pop('industry', None),
            'location': validated_data.pop('location', None),
        }

        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'],
            password=validated_data['password'],
            user_type=validated_data['user_type'],
            phone_number=validated_data.get('phone_number', None)
        )

        if user.user_type == 'job_seeker':
            JobSeeker.objects.create(user=user, expected_salary=0)
        elif user.user_type == 'job_provider':
            JobProvider.objects.create(
                user=user,
                company_name=job_provider_data['company_name'] or '',
                company_website=job_provider_data['company_website'],
                description=job_provider_data['description'],
                company_logo=job_provider_data['company_logo'],
                industry=job_provider_data['industry'] or '',
                location=job_provider_data['location']
            )

        return user

class JobSeekerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    class Meta:
        model = JobSeeker
        fields = ['user', 'resume', 'summary', 'experience', 'current_salary', 'expected_salary', 'is_available']
class JobProviderProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only = True)
    class Meta:
        model = JobProvider
        fields = ['user', 'company_name', 'company_logo', 'industry', 'company_website', 'description', 'location']

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with the email exists")
        return value
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only = True)
    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        cache_key = f"otp_{email}"
        stored_otp = cache.get(cache_key)
        if not stored_otp or stored_otp != otp:
            
            raise serializers.ValidationError("Invalid or expired OTP.")
        return data
    
    def save(self):
        email = self.validated_data['email']
        new_password = self.validated_data['new_password']
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        cache.delete(f"otp_{email}")
        return user
    
class SendVerificationOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user with this email exists.")
        if User.objects.get(email=value).is_verified:
            raise serializers.ValidationError("Email is already verified.")
        return value

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        email = data.get('email')
        otp = data.get('otp')
        cache_key = f"verification_otp_{email}"
        stored_otp = cache.get(cache_key)

        if not stored_otp or stored_otp != otp:
            raise serializers.ValidationError("Invalid or expired OTP.")
        return data

    def save(self):
        email = self.validated_data['email']
        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()
        cache.delete(f"verification_otp_{email}") 
        return user
