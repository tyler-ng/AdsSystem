from django.contrib import admin
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Count, F, Sum, Case, When, IntegerField, FloatField
from django.db.models.functions import Coalesce
from django.utils.safestring import mark_safe
from .models import Campaign, Creative, Target, AdImpression, AdClick, Placement


class TargetInline(admin.StackedInline):
    model = Target
    extra = 1
    fieldsets = (
        ('Device Targeting', {
            'fields': ('os_android', 'os_ios', 'os_version_min', 'os_version_max')
        }),
        ('Demographic Targeting', {
            'fields': ('gender', 'age_min', 'age_max')
        }),
        ('Location Targeting', {
            'fields': ('countries', 'regions', 'cities')
        }),
        ('Interest Targeting', {
            'fields': ('interests',)
        }),
    )


class CreativeInline(admin.StackedInline):
    model = Creative
    extra = 1
    fieldsets = (
        (None, {
            'fields': ('name', 'type', 'placement', 'is_active')
        }),
        ('Creative Content', {
            'fields': ('title', 'description', 'image', 'video', 'call_to_action', 'destination_url')
        }),
        ('Dimensions', {
            'fields': ('width', 'height')
        }),
    )


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'advertiser', 'status', 'start_date', 'end_date', 'daily_budget', 'is_active', 'view_analytics')
    list_filter = ('status', 'start_date', 'end_date', 'company_name')
    search_fields = ('name', 'advertiser__username', 'company_name')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [TargetInline, CreativeInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'company_name', 'advertiser', 'status', 'description')
        }),
        ('Budget & Schedule', {
            'fields': ('start_date', 'end_date', 'daily_budget', 'total_budget')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def view_analytics(self, obj):
        """Add a link to view analytics for this campaign"""
        return mark_safe(f'<a href="{obj.id}/analytics/" class="button">View Analytics</a>')
    view_analytics.short_description = 'Analytics'
    view_analytics.allow_tags = True

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<uuid:campaign_id>/analytics/', 
                 self.admin_site.admin_view(self.campaign_analytics_view), 
                 name='campaign-analytics'),
        ]
        return custom_urls + urls

    def campaign_analytics_view(self, request, campaign_id):
        """Custom admin view to display campaign analytics"""
        campaign = self.get_object(request, campaign_id)
        
        # Get basic analytics data
        impressions_count = AdImpression.objects.filter(campaign=campaign).count()
        clicks_count = AdClick.objects.filter(campaign=campaign).count()
        ctr = round((clicks_count / impressions_count * 100) if impressions_count > 0 else 0, 2)
        
        # Get creative-level analytics
        creatives_data = Creative.objects.filter(campaign=campaign).annotate(
            impression_count=Count('impressions', distinct=True),
            click_count=Count('clicks', distinct=True),
            ctr_value=Case(
                When(impression_count__gt=0, 
                     then=100.0 * F('click_count') / F('impression_count')),
                default=0.0,
                output_field=FloatField()
            )
        ).values('id', 'name', 'type', 'impression_count', 'click_count', 'ctr_value')
        
        # Get country analytics
        country_data = AdImpression.objects.filter(campaign=campaign).values(
            'country'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get device analytics
        device_data = AdImpression.objects.filter(campaign=campaign).values(
            'device_type'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get OS analytics
        os_data = AdImpression.objects.filter(campaign=campaign).values(
            'os'
        ).annotate(
            count=Count('id')
        ).order_by('-count')
        
        context = {
            **self.admin_site.each_context(request),
            'opts': self.model._meta,
            'campaign': campaign,
            'title': f'Analytics for {campaign.name}',
            'impressions': impressions_count,
            'clicks': clicks_count,
            'ctr': ctr,
            'creatives_data': creatives_data,
            'country_data': country_data,
            'device_data': device_data,
            'os_data': os_data,
        }
        
        return TemplateResponse(
            request, 
            'admin/advertising/campaign/analytics.html', 
            context
        )


@admin.register(Creative)
class CreativeAdmin(admin.ModelAdmin):
    list_display = ('name', 'campaign', 'placement', 'type', 'is_active')
    list_filter = ('type', 'is_active', 'campaign', 'placement')
    search_fields = ('name', 'campaign__name', 'placement__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('campaign', 'name', 'type', 'placement', 'is_active')
        }),
        ('Creative Content', {
            'fields': ('title', 'description', 'image', 'video', 'call_to_action', 'destination_url')
        }),
        ('Dimensions', {
            'fields': ('width', 'height')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'recommended_width', 'recommended_height', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('name', 'code', 'description', 'is_active')
        }),
        ('Recommended Dimensions', {
            'fields': ('recommended_width', 'recommended_height')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'gender', 'os_android', 'os_ios')
    list_filter = ('gender', 'os_android', 'os_ios')
    search_fields = ('campaign__name',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('campaign',)
        }),
        ('Device Targeting', {
            'fields': ('os_android', 'os_ios', 'os_version_min', 'os_version_max')
        }),
        ('Demographic Targeting', {
            'fields': ('gender', 'age_min', 'age_max')
        }),
        ('Location Targeting', {
            'fields': ('countries', 'regions', 'cities')
        }),
        ('Interest Targeting', {
            'fields': ('interests',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):
    list_display = ('creative', 'campaign', 'timestamp', 'country', 'device_type', 'os')
    list_filter = ('timestamp', 'country', 'device_type', 'os')
    search_fields = ('campaign__name', 'creative__name')
    readonly_fields = ('timestamp',)
    fieldsets = (
        ('Ad Reference', {
            'fields': ('creative', 'campaign')
        }),
        ('Device Information', {
            'fields': ('device_type', 'os', 'os_version', 'app_id', 'app_version')
        }),
        ('Location', {
            'fields': ('ip_address', 'country', 'region', 'city')
        }),
        ('Metadata', {
            'fields': ('user_agent', 'timestamp')
        }),
    )


@admin.register(AdClick)
class AdClickAdmin(admin.ModelAdmin):
    list_display = ('creative', 'campaign', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('campaign__name', 'creative__name')
    readonly_fields = ('timestamp',)
    fieldsets = (
        ('Ad Reference', {
            'fields': ('impression', 'creative', 'campaign')
        }),
        ('Metadata', {
            'fields': ('timestamp',)
        }),
    ) 