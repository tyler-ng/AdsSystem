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

from .models import Campaign, Creative, Target, AdImpression, AdClick, Placement
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
        
        # Try to get cached ads for this app (cached per app_id)
        cache_key = f"mobile_ads_{app_id}_{'-'.join(ad_types)}"
        cached_ads = cache.get(cache_key)
        
        if cached_ads:
            # Log impression asynchronously
            self._log_impression(request, cached_ads[0], ad_data)
            return Response(cached_ads)
        
        # Get relevant ads for this request
        ads = self._get_relevant_ads(ad_data, ad_types, limit)
        
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
    
    def _get_relevant_ads(self, ad_data, ad_types, limit):
        """Find relevant ads based on targeting criteria"""
        now = timezone.now()
        
        # Base query for active campaigns with active creatives
        base_query = Q(
            campaign__status='active',
            campaign__start_date__lte=now,
            is_active=True,
            type__in=ad_types
        ) & (
            Q(campaign__end_date__isnull=True) | 
            Q(campaign__end_date__gt=now)
        )
        
        # Device targeting
        os_name = ad_data.get('os', '').lower()
        os_version = ad_data.get('os_version', '')
        
        device_query = Q()
        if os_name == 'android':
            device_query &= Q(campaign__targets__os_android=True)
        elif os_name == 'ios':
            device_query &= Q(campaign__targets__os_ios=True)
        
        # If provided, add OS version constraints
        if os_version and os_name:
            device_query &= (
                Q(campaign__targets__os_version_min='') | 
                Q(campaign__targets__os_version_min__lte=os_version)
            ) & (
                Q(campaign__targets__os_version_max='') | 
                Q(campaign__targets__os_version_max__gte=os_version)
            )
        
        # Demographic targeting
        demo_query = Q()
        if 'gender' in ad_data and ad_data['gender']:
            demo_query &= (
                Q(campaign__targets__gender='all') | 
                Q(campaign__targets__gender=ad_data['gender'])
            )
        
        if 'age' in ad_data and ad_data['age']:
            age = ad_data['age']
            demo_query &= (
                (Q(campaign__targets__age_min__isnull=True) | Q(campaign__targets__age_min__lte=age)) &
                (Q(campaign__targets__age_max__isnull=True) | Q(campaign__targets__age_max__gte=age))
            )
        
        # Location targeting
        location_query = Q()
        if 'country' in ad_data and ad_data['country']:
            country = ad_data['country'].upper()
            location_query &= (
                Q(campaign__targets__countries=[]) | 
                Q(campaign__targets__countries__contains=[country])
            )
        
        # Interest targeting
        interest_query = Q()
        if 'interests' in ad_data and ad_data['interests']:
            # Find campaigns that target any of the user interests
            interests = ad_data['interests']
            # This is a simplification - in production, you'd use more sophisticated interest matching
            interest_query &= Q(campaign__targets__interests__overlap=interests)
        
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
        final_query = base_query & device_query & demo_query & location_query & interest_query & size_query
        
        # Get ads, ordered by newest campaigns first
        ads = Creative.objects.filter(final_query).select_related('campaign').order_by('-campaign__created_at')[:limit]
        
        return list(ads)
    
    @transaction.atomic
    def _log_impression(self, request, ad, ad_data):
        """Log an ad impression"""
        client_ip, is_routable = get_client_ip(request)
        
        impression = AdImpression.objects.create(
            creative_id=ad.id,
            campaign_id=ad.campaign_id,
            ip_address=client_ip,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            device_type=ad_data.get('device_type', ''),
            os=ad_data.get('os', ''),
            os_version=ad_data.get('os_version', ''),
            country=ad_data.get('country', ''),
            region=ad_data.get('region', ''),
            city=ad_data.get('city', ''),
            app_id=ad_data.get('app_id', ''),
            app_version=ad_data.get('app_version', '')
        )
        
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