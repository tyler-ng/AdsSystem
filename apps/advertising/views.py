from typing import List, Dict, Any
from django.db.models import Q
from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.authentication import JWTAuthentication
from asgiref.sync import sync_to_async
from ipware import get_client_ip
import hashlib
import uuid
from decimal import Decimal

from .models import Campaign, Creative, Target, AdImpression, AdClick, Placement, AdOpportunity, DailySpending
from .serializers import (
    CampaignSerializer, CampaignListSerializer, CreativeSerializer, 
    TargetSerializer, AdImpressionSerializer, AdClickSerializer,
    AdRequestSerializer, MobileAdSerializer, PlacementSerializer
)


class CampaignPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CampaignViewSet(ModelViewSet):
    """ViewSet for managing campaigns"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CampaignPagination
    queryset = Campaign.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return CampaignListSerializer
        return CampaignSerializer
    
    def get_queryset(self):
        user = self.request.user
        # Admin can see all campaigns
        if user.is_staff:
            return Campaign.objects.all()
        # Regular users can only see their own campaigns
        return Campaign.objects.filter(advertiser=user)
    
    def perform_create(self, serializer):
        serializer.save(advertiser=self.request.user)


class CreativeViewSet(ModelViewSet):
    """ViewSet for managing creatives"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = CreativeSerializer
    
    def get_queryset(self):
        user = self.request.user
        campaign_id = self.kwargs.get('campaign_pk')
        
        if user.is_staff:
            return Creative.objects.filter(campaign_id=campaign_id)
        
        return Creative.objects.filter(
            campaign_id=campaign_id,
            campaign__advertiser=user
        )
    
    def perform_create(self, serializer):
        campaign_id = self.kwargs.get('campaign_pk')
        serializer.save(campaign_id=campaign_id)


class TargetViewSet(ModelViewSet):
    """ViewSet for managing targeting"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TargetSerializer
    
    def get_queryset(self):
        user = self.request.user
        campaign_id = self.kwargs.get('campaign_pk')
        
        if user.is_staff:
            return Target.objects.filter(campaign_id=campaign_id)
        
        return Target.objects.filter(
            campaign_id=campaign_id,
            campaign__advertiser=user
        )
    
    def perform_create(self, serializer):
        campaign_id = self.kwargs.get('campaign_pk')
        serializer.save(campaign_id=campaign_id)


class PlacementViewSet(ModelViewSet):
    """ViewSet for managing ad placements"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PlacementSerializer
    queryset = Placement.objects.all()
    
    def get_queryset(self):
        user = self.request.user
        # Only admin users can see all placements
        if user.is_staff:
            return Placement.objects.all()
        # Regular users can still see active placements
        return Placement.objects.filter(is_active=True)


class MobileAdServingView(APIView):
    """
    View for serving ads to mobile apps.
    Optimized for performance with caching.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = AdRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract ad request data
        ad_data = serializer.validated_data
        app_id = ad_data.get('app_id')
        ad_types = ad_data.get('ad_types', ['banner', 'interstitial', 'native'])
        limit = ad_data.get('limit', 1)
        
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Try to get cached ads for this app (cached per app_id)
        cache_key = f"mobile_ads_{app_id}_{'-'.join(ad_types)}"
        cached_ads = cache.get(cache_key)
        
        if cached_ads:
            # Log impression asynchronously
            self._log_impression(request, cached_ads[0], ad_data)
            return Response(cached_ads)
        
        # Get eligible campaigns for this request
        eligible_campaigns = self._get_eligible_campaigns(ad_data, ad_types)
        
        # Track ad opportunities for sampled requests
        self._track_opportunities(request_id, eligible_campaigns, ad_data)
        
        # Get relevant ads for this request
        ads = self._get_relevant_ads(ad_data, ad_types, limit, eligible_campaigns)
        
        if not ads:
            return Response({"detail": "No matching ads found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize for mobile
        serializer = MobileAdSerializer(ads, many=True, context={'request': request})
        response_data = serializer.data
        
        # Cache ads for this app_id for 5 minutes
        cache.set(cache_key, response_data, timeout=300)
        
        # Log impression
        self._log_impression(request, ads[0], ad_data)
        
        return Response(response_data)
    
    def _get_eligible_campaigns(self, ad_data, ad_types):
        """Find all campaigns that are eligible for this request"""
        now = timezone.now()
        
        # Base query for active campaigns
        base_query = Q(
            status='active',
            start_date__lte=now
        ) & (
            Q(end_date__isnull=True) | 
            Q(end_date__gt=now)
        )
        
        # Device targeting
        os_name = ad_data.get('os', '').lower()
        os_version = ad_data.get('os_version', '')
        
        device_query = Q()
        if os_name == 'android':
            device_query &= Q(targets__os_android=True)
        elif os_name == 'ios':
            device_query &= Q(targets__os_ios=True)
        
        # If provided, add OS version constraints
        if os_version and os_name:
            device_query &= (
                Q(targets__os_version_min='') | 
                Q(targets__os_version_min__lte=os_version)
            ) & (
                Q(targets__os_version_max='') | 
                Q(targets__os_version_max__gte=os_version)
            )
        
        # Demographics targeting
        demo_query = Q()
        gender = ad_data.get('gender', '')
        age = ad_data.get('age')
        
        if gender:
            demo_query &= (
                Q(targets__gender='all') | 
                Q(targets__gender=gender)
            )
        
        if age:
            demo_query &= (
                Q(targets__age_min__isnull=True) | Q(targets__age_min__lte=age)
            ) & (
                Q(targets__age_max__isnull=True) | Q(targets__age_max__gte=age)
            )
        
        # Geographic targeting
        geo_query = Q()
        country = ad_data.get('country', '').upper()
        region = ad_data.get('region', '')
        city = ad_data.get('city', '')
        
        if country:
            geo_query &= (
                Q(targets__countries=[]) | 
                Q(targets__countries__contains=[country])
            )
        
        if region:
            geo_query &= (
                Q(targets__regions=[]) | 
                Q(targets__regions__contains=[region])
            )
        
        if city:
            geo_query &= (
                Q(targets__cities=[]) | 
                Q(targets__cities__contains=[city])
            )
        
        # Interest targeting
        interests = ad_data.get('interests', [])
        interest_query = Q()
        
        if interests:
            # Match any of the provided interests
            for interest in interests:
                interest_query |= Q(targets__interests__contains=[interest])
        
        # Combine all filters and get campaigns
        campaigns = Campaign.objects.filter(
            base_query & device_query & demo_query & geo_query
        ).distinct()
        
        # Apply interest filter separately if provided
        if interests:
            campaigns = campaigns.filter(interest_query)
        
        # Filter campaigns that haven't exceeded daily budget
        eligible_campaigns = []
        estimated_cost = Decimal('0.01')  # Estimated cost per impression
        
        for campaign in campaigns:
            # Check if campaign can show ads (not paused for budget and has budget available)
            if not campaign.is_paused_for_day() and campaign.can_show_ad(estimated_cost):
                eligible_campaigns.append(campaign)
        
        return eligible_campaigns
    
    def _track_opportunities(self, request_id, eligible_campaigns, ad_data):
        """Track ad opportunities for sampled requests"""
        if not eligible_campaigns:
            return
            
        # Get the first eligible placement that matches the request
        placement = None
        if 'width' in ad_data and 'height' in ad_data and ad_data['width'] and ad_data['height']:
            width = ad_data.get('width')
            height = ad_data.get('height')
            placement = Placement.objects.filter(
                Q(recommended_width__lte=width) & 
                Q(recommended_height__lte=height)
            ).first()
        
        if not placement:
            # Default to first active placement
            placement = Placement.objects.filter(is_active=True).first()
            
        if not placement:
            return
            
        # For each eligible campaign, determine if we should track this opportunity
        for campaign in eligible_campaigns:
            # Use the campaign's sampling rate to determine if we should track this opportunity
            sampling_rate = campaign.opportunity_sampling_rate
            
            # Create a hash of the request ID and campaign ID for consistent sampling
            hash_input = f"{request_id}:{campaign.id}"
            hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
            
            # If the hash value falls within the sampling rate, track the opportunity
            if hash_value % 100 < sampling_rate:
                # The selected campaign is the one that will be shown
                selected_campaign = eligible_campaigns.first()
                was_shown = (campaign.id == selected_campaign.id) if selected_campaign else False
                
                # Record the opportunity
                AdOpportunity.objects.create(
                    campaign=campaign,
                    placement=placement,
                    was_shown=was_shown,
                    request_id=request_id,
                    device_type=ad_data.get('device_type', ''),
                    os=ad_data.get('os', ''),
                    country=ad_data.get('country', '')
                )
    
    def _get_relevant_ads(self, ad_data, ad_types, limit, eligible_campaigns=None):
        """Find relevant ads based on targeting criteria"""
        now = timezone.now()
        
        if eligible_campaigns is None:
            eligible_campaigns = self._get_eligible_campaigns(ad_data, ad_types)
        
        # Base query for creatives
        base_query = Q(
            campaign__in=eligible_campaigns,
            is_active=True,
            type__in=ad_types
        )
        
        # Size constraints for banner ads
        size_query = Q()
        if 'width' in ad_data and 'height' in ad_data:
            width = ad_data.get('width')
            height = ad_data.get('height')
            if width and height:
                size_query &= (
                    Q(width__isnull=True) | Q(height__isnull=True) |
                    (Q(width__lte=width) & Q(height__lte=height))
                )
        
        # Combine all criteria
        final_query = base_query & size_query
        
        # Get ads, ordered by newest campaigns first
        ads = Creative.objects.filter(final_query).select_related('campaign').order_by('-campaign__created_at')[:limit]
        
        return list(ads)
    
    @transaction.atomic
    def _log_impression(self, request, ad, ad_data):
        """Log an ad impression and record spending"""
        ip_address, is_routable = get_client_ip(request)
        
        # Create impression record
        impression = AdImpression.objects.create(
            creative=ad,
            campaign=ad.campaign,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_type=ad_data.get('device_type', ''),
            os=ad_data.get('os', ''),
            os_version=ad_data.get('os_version', ''),
            country=ad_data.get('country', ''),
            region=ad_data.get('region', ''),
            city=ad_data.get('city', ''),
            app_id=ad_data.get('app_id', ''),
            app_version=ad_data.get('app_version', ''),
        )
        
        # Record spending for this impression
        impression_cost = Decimal('0.01')  # You can make this configurable
        try:
            daily_spending = ad.campaign.record_spending(impression_cost)
            
            # Log if budget was exceeded
            if daily_spending.budget_exceeded:
                print(f"Campaign {ad.campaign.name} exceeded daily budget and was paused")
                
        except Exception as e:
            print(f"Error recording spending for campaign {ad.campaign.name}: {e}")
        
        return impression


class LogAdClickView(APIView):
    """View for logging ad clicks"""
    permission_classes = [AllowAny]
    
    def post(self, request, ad_id):
        try:
            creative = Creative.objects.get(id=ad_id)
            self._create_click(creative)
            return Response({"status": "success"})
        except Creative.DoesNotExist:
            return Response({"detail": "Ad not found"}, status=status.HTTP_404_NOT_FOUND)
    
    @transaction.atomic
    def _create_click(self, creative):
        """Create an ad click record"""
        click = AdClick.objects.create(
            creative=creative,
            campaign=creative.campaign
        )
        return click


class AnalyticsView(APIView):
    """View for retrieving ad performance analytics"""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, campaign_id=None):
        user = request.user
        
        if campaign_id:
            # Get stats for specific campaign
            campaign = self._get_campaign(user, campaign_id)
            if not campaign:
                return Response({"detail": "Campaign not found"}, status=status.HTTP_404_NOT_FOUND)
                
            stats = self._get_campaign_stats(campaign)
            return Response(stats)
        else:
            # Get stats for all user's campaigns
            if user.is_staff:
                campaign_ids = Campaign.objects.values_list('id', flat=True)
            else:
                campaign_ids = Campaign.objects.filter(advertiser=user).values_list('id', flat=True)
                
            stats = self._get_campaigns_stats(campaign_ids)
            return Response(stats)
    
    def _get_campaign(self, user, campaign_id):
        """Get a campaign with permission check"""
        if user.is_staff:
            return Campaign.objects.get(id=campaign_id)
        return Campaign.objects.get(id=campaign_id, advertiser=user)
    
    def _get_campaign_stats(self, campaign):
        """Get performance stats for a single campaign"""
        impression_count = AdImpression.objects.filter(campaign=campaign).count()
        click_count = AdClick.objects.filter(campaign=campaign).count()
        ctr = (click_count / impression_count * 100) if impression_count > 0 else 0
        
        # Get display rate stats
        today = timezone.now().date()
        opportunities = AdOpportunity.objects.filter(campaign=campaign, timestamp__date=today).count()
        shown = AdOpportunity.objects.filter(campaign=campaign, timestamp__date=today, was_shown=True).count()
        display_rate = (shown / opportunities * 100) if opportunities > 0 else 0
        
        # Get stats per creative
        creative_stats = []
        for creative in Creative.objects.filter(campaign=campaign):
            c_impressions = AdImpression.objects.filter(creative=creative).count()
            c_clicks = AdClick.objects.filter(creative=creative).count()
            c_ctr = (c_clicks / c_impressions * 100) if c_impressions > 0 else 0
            
            creative_stats.append({
                'id': creative.id,
                'name': creative.name,
                'type': creative.type,
                'impressions': c_impressions,
                'clicks': c_clicks,
                'ctr': round(c_ctr, 2)
            })
        
        return {
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'company_name': campaign.company_name,
            'status': campaign.status,
            'impressions': impression_count,
            'clicks': click_count,
            'ctr': round(ctr, 2),
            'display_rate': round(display_rate, 2),
            'sampled_opportunities': opportunities,
            'creatives': creative_stats
        }
    
    def _get_campaigns_stats(self, campaign_ids):
        """Get performance stats for multiple campaigns"""
        stats = []
        for campaign_id in campaign_ids:
            try:
                campaign = Campaign.objects.get(id=campaign_id)
                campaign_stats = self._get_campaign_stats(campaign)
                stats.append(campaign_stats)
            except Campaign.DoesNotExist:
                continue
        
        return stats 