from rest_framework import serializers
from .models import Campaign, Creative, Target, AdImpression, AdClick, Placement
from django.conf import settings


class PlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Placement
        fields = [
            'id', 'name', 'code', 'description', 'recommended_width', 
            'recommended_height', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


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
    placement_details = PlacementSerializer(source='placement', read_only=True)
    image_url = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Creative
        fields = [
            'id', 'name', 'type', 'placement', 'placement_details', 'title', 
            'description', 'image', 'video', 'image_url', 'video_url', 'call_to_action', 'destination_url', 
            'width', 'height', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'image_url', 'video_url']
    
    def get_image_url(self, obj):
        """Return absolute URL for image download"""
        if not obj.image or not obj.image.name:
            return None
        
        try:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            
            # Fallback if request is not available (using settings)
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            return f"{base_url}{obj.image.url}"
        except (ValueError, AttributeError):
            # Handle case where image field exists but no file is associated
            return None
    
    def get_video_url(self, obj):
        """Return absolute URL for video download"""
        if not obj.video or not obj.video.name:
            return None
        
        try:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
            
            # Fallback if request is not available (using settings)
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            return f"{base_url}{obj.video.url}"
        except (ValueError, AttributeError):
            # Handle case where video field exists but no file is associated
            return None


class CampaignSerializer(serializers.ModelSerializer):
    targets = TargetSerializer(many=True, required=False, read_only=True)
    creatives = CreativeSerializer(many=True, required=False, read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    campaign_images = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'company_name', 'advertiser', 'status', 'start_date', 'end_date',
            'daily_budget', 'total_budget', 'budget_exceeded_action', 'budget_exceeded_frequency_cap',
            'opportunity_sampling_rate', 'description', 'created_at',
            'updated_at', 'targets', 'creatives', 'campaign_images', 'is_active'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_active', 'advertiser', 'campaign_images']
    
    def get_campaign_images(self, obj):
        """Return all image URLs from campaign creatives for easy mobile access"""
        images = []
        for creative in obj.creatives.filter(is_active=True, image__isnull=False):
            # Skip creatives where image field exists but has no file
            if not creative.image.name:
                continue
                
            try:
                request = self.context.get('request')
                if request:
                    image_url = request.build_absolute_uri(creative.image.url)
                else:
                    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
                    image_url = f"{base_url}{creative.image.url}"
                
                images.append({
                    'creative_id': str(creative.id),
                    'creative_name': creative.name,
                    'creative_type': creative.type,
                    'image_url': image_url,
                    'width': creative.width,
                    'height': creative.height,
                    'title': creative.title,
                    'description': creative.description,
                    'call_to_action': creative.call_to_action,
                    'destination_url': creative.destination_url
                })
            except (ValueError, AttributeError):
                # Skip creatives with invalid image files
                continue
        return images


class CampaignListSerializer(serializers.ModelSerializer):
    """Simplified serializer for listing campaigns"""
    is_active = serializers.BooleanField(read_only=True)
    primary_image = serializers.SerializerMethodField()
    images_count = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'id', 'name', 'company_name', 'status', 'start_date', 'end_date',
            'daily_budget', 'total_budget', 'budget_exceeded_action', 
            'created_at', 'is_active', 'primary_image', 'images_count'
        ]
        read_only_fields = ['id', 'created_at', 'is_active', 'primary_image', 'images_count']
    
    def get_primary_image(self, obj):
        """Return the first available image URL for mobile display"""
        first_creative = obj.creatives.filter(is_active=True, image__isnull=False).first()
        if not first_creative or not first_creative.image or not first_creative.image.name:
            return None
        
        try:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(first_creative.image.url)
            
            # Fallback if request is not available
            base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
            return f"{base_url}{first_creative.image.url}"
        except (ValueError, AttributeError):
            # Handle case where image field exists but no file is associated
            return None
    
    def get_images_count(self, obj):
        """Return the total number of images in this campaign"""
        return obj.creatives.filter(is_active=True, image__isnull=False).count()


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
    placement_code = serializers.CharField(source='placement.code', read_only=True, allow_null=True)
    
    class Meta:
        model = Creative
        fields = [
            'id', 'campaign_id', 'ad_type', 'title', 'description', 
            'image_url', 'video_url', 'cta', 'action_url', 'width', 'height',
            'placement_code'
        ]
    
    def get_image_url(self, obj):
        """Return absolute URL for image"""
        if not obj.image or not obj.image.name:
            return None
        
        try:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            
            # Fallback if request is not available (using settings)
            base_url = getattr(settings, 'BASE_URL', None)
            if base_url:
                return f"{base_url}{obj.image.url}"
            
            return obj.image.url
        except (ValueError, AttributeError):
            # Handle case where image field exists but no file is associated
            return None
    
    def get_video_url(self, obj):
        """Return absolute URL for video"""
        if not obj.video or not obj.video.name:
            return None
        
        try:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.video.url)
            
            # Fallback if request is not available (using settings)
            base_url = getattr(settings, 'BASE_URL', None)
            if base_url:
                return f"{base_url}{obj.video.url}"
            
            return obj.video.url
        except (ValueError, AttributeError):
            # Handle case where video field exists but no file is associated
            return None 