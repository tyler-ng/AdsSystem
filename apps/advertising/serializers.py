from rest_framework import serializers
from .models import Campaign, Creative, Target, AdImpression, AdClick
from django.conf import settings


class TargetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Target
        fields = [
            'id', 'os_android', 'os_ios', 'os_version_min', 'os_version_max',
            'gender', 'age_min', 'age_max', 'countries', 'regions', 'cities',
            'interests', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CreativeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creative
        fields = [
            'id', 'name', 'type', 'title', 'description', 'image', 'video',
            'call_to_action', 'destination_url', 'width', 'height', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CampaignSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True, required=False, read_only=True)
    creatives = CreativeSerializer(many=True, required=False, read_only=True)
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'company_name', 'advertiser', 'status', 'start_date', 'end_date',
            'daily_budget', 'total_budget', 'description', 'created_at',
            'updated_at', 'targets', 'creatives', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active', 'advertiser']


class CampaignListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing campaigns"""
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'company_name', 'status', 'start_date', 'end_date',
            'daily_budget', 'total_budget', 'created_at', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'is_active']


class AdImpressionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdImpression
        fields = [
            'id', 'creative', 'campaign', 'ip_address', 'user_agent',
            'device_type', 'os', 'os_version', 'country', 'region', 'city',
            'timestamp', 'app_id', 'app_version'
        ]
        read_only_fields = ['id', 'timestamp']


class AdClickSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdClick
        fields = ['id', 'impression', 'creative', 'campaign', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class AdRequestSerializer(serializers.Serializer):
    """Serializer for ad request from mobile app"""
    app_id = serializers.CharField(required=True, max_length=255)
    app_version = serializers.CharField(required=True, max_length=50)
    os = serializers.CharField(required=True, max_length=50)
    os_version = serializers.CharField(required=True, max_length=20)
    device_type = serializers.CharField(required=True, max_length=50)
    width = serializers.IntegerField(required=False)
    height = serializers.IntegerField(required=False)
    country = serializers.CharField(required=False, max_length=2)
    region = serializers.CharField(required=False, max_length=100)
    city = serializers.CharField(required=False, max_length=100)
    gender = serializers.CharField(required=False, max_length=10)
    age = serializers.IntegerField(required=False)
    interests = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False
    )
    ad_types = serializers.ListField(
        child=serializers.CharField(max_length=20),
        required=False,
        default=['banner', 'interstitial', 'native']
    )
    limit = serializers.IntegerField(required=False, default=1)


class MobileAdSerializer(serializers.ModelSerializer):
    """Simplified serializer for mobile ad response"""
    campaign_id = serializers.UUIDField(source='campaign.id')
    ad_type = serializers.CharField(source='type')
    cta = serializers.CharField(source='call_to_action')
    action_url = serializers.URLField(source='destination_url')
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Creative
        fields = [
            'id', 'campaign_id', 'ad_type', 'title', 'description', 
            'image_url', 'video_url', 'cta', 'action_url', 'width', 'height'
        ]
    
    def get_image_url(self, obj):
        """Return absolute URL for image"""
        if not obj.image:
            return None
        
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.image.url)
        
        # Fallback if request is not available (using settings)
        base_url = getattr(settings, 'BASE_URL', None)
        if base_url:
            return f"{base_url}{obj.image.url}"
        
        return obj.image.url if obj.image else None
    
    def get_video_url(self, obj):
        """Return absolute URL for video"""
        if not obj.video:
            return None
        
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.video.url)
        
        # Fallback if request is not available (using settings)
        base_url = getattr(settings, 'BASE_URL', None)
        if base_url:
            return f"{base_url}{obj.video.url}"
        
        return obj.video.url if obj.video else None 