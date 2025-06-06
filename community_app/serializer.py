# community/serializers.py
from rest_framework import serializers
from .models import Community, CommunityMember, CommunityMessage, UserReadStatus
from auth_app.models import User
from cloudinary.utils import cloudinary_url

class CommunitySerializer(serializers.ModelSerializer):
    cover_image_url = serializers.SerializerMethodField()
    class Meta:
        model = Community
        fields = ['id', 'name', 'description', 'cover_image','cover_image_url', 'category', 'created_at']
    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url
        return None

class CommunityMemberSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    community_name = serializers.CharField(source='community.name', read_only=True)

    class Meta:
        model = CommunityMember
        fields = ['id', 'community', 'community_name', 'user', 'joined_at']

class CommunityMessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(slug_field='username', read_only=True)
    
    class Meta:
        model = CommunityMessage
        fields = ['id', 'community', 'sender', 'sender_id', 'content', 'attachment', 'created_at']
        read_only_fields = ['sender']
    
    def create(self, validated_data):
        # Remove sender_id if present since it's only for validation
        validated_data.pop('sender_id', None)
        return super().create(validated_data)
    
class UserReadStatusSerializer(serializers.ModelSerializer):
    unread_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = UserReadStatus
        fields = ['id', 'user', 'community', 'last_read_message', 'last_read_time', 'unread_count']
        read_only_fields = ['user', 'last_read_time']