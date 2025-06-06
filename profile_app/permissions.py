from rest_framework.permissions import BasePermission
from auth_app.models import JobSeeker,JobProvider

class IsJobSeeker(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_authenticated and hasattr(request.user, 'job_seeker_profile') and request.user.job_seeker_profile is not None
        except JobSeeker.DoesNotExist:
            return False
class IsJobProvier(BasePermission):
    def has_permission(self, request, view):
        try:
            return request.user.is_authenticated and hasattr(request.user, 'job_provider_profile') and request.user.job_provider_profile is not None
        except JobProvider.DoesNotExist:
            return False