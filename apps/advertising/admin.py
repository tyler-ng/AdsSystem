from django.contrib import admin
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.urls import path
from django.db.models import Count, F, Sum, Case, When, IntegerField, FloatField
from django.db.models.functions import Coalesce
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Campaign, Creative, Target, AdImpression, AdClick, Placement, AdOpportunity, DailySpending


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


class DailySpendingInline(admin.TabularInline):
    model = DailySpending
    extra = 0
    readonly_fields = ('date', 'amount_spent', 'remaining_budget', 'budget_exceeded', 'created_at')
    can_delete = False
    
    def remaining_budget(self, obj):
        return obj.remaining_budget
    remaining_budget.short_description = 'Remaining Budget'


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'company_name', 'advertiser', 'status', 'budget_exceeded_action',
                   'daily_budget', 'spent_today', 'remaining_today', 'display_rate_formatted', 
                   'impressions_today_count', 'start_date', 'is_active', 'view_analytics')
    list_filter = ('status', 'budget_exceeded_action', 'start_date', 'end_date', 'company_name')
    search_fields = ('name', 'advertiser__username', 'company_name')
    readonly_fields = ('created_at', 'updated_at', 'display_rate_formatted', 'impressions_today_count',
                      'spent_today', 'remaining_today', 'budget_status')
    inlines = [TargetInline, CreativeInline, DailySpendingInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'company_name', 'advertiser', 'status', 'description')
        }),
        ('Budget Configuration', {
            'fields': ('daily_budget', 'total_budget', 'budget_exceeded_action', 'budget_exceeded_frequency_cap'),
            'description': 'Configure how the campaign behaves when daily budget limits are reached.'
        }),
        ('Display Settings', {
            'fields': ('opportunity_sampling_rate',)
        }),
        ('Performance Metrics', {
            'fields': ('display_rate_formatted', 'impressions_today_count')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Daily Budget Status', {
            'fields': ('spent_today', 'remaining_today', 'budget_status')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def spent_today(self, obj):
        """Show amount spent today"""
        amount = obj.get_daily_spending()
        return f"${amount:.2f}"
    spent_today.short_description = 'Spent Today'
    
    def remaining_today(self, obj):
        """Show remaining daily budget"""
        spent = obj.get_daily_spending()
        remaining = obj.daily_budget - spent
        return f"${remaining:.2f}"
    remaining_today.short_description = 'Remaining Today'
    
    def budget_status(self, obj):
        """Show budget status with color coding and action info"""
        if obj.is_paused_for_day():
            action_text = obj.get_budget_exceeded_action_display()
            return mark_safe(f'<span style="color: red; font-weight: bold;">EXCEEDED - {action_text}</span>')
        
        spent = obj.get_daily_spending()
        remaining = obj.daily_budget - spent
        percentage_spent = (spent / obj.daily_budget) * 100 if obj.daily_budget > 0 else 0
        
        if percentage_spent >= 90:
            color = "red"
            status = f"WARNING - {percentage_spent:.1f}% spent"
        elif percentage_spent >= 70:
            color = "orange" 
            status = f"MODERATE - {percentage_spent:.1f}% spent"
        else:
            color = "green"
            status = f"GOOD - {percentage_spent:.1f}% spent"
        
        action_text = obj.get_budget_exceeded_action_display()
        return mark_safe(
            f'<span style="color: {color}; font-weight: bold;">{status}</span><br>'
            f'<small>On exceed: {action_text}</small>'
        )
    budget_status.short_description = 'Budget Status'

    def display_rate_formatted(self, obj):
        """Format the display rate as a percentage"""
        rate = obj.display_rate_today
        today = timezone.now().date()
        opportunities = obj.opportunities.filter(timestamp__date=today).count()
        
        if opportunities == 0:
            return "No data (0 sampled opportunities)"
        
        sampling_rate = obj.opportunity_sampling_rate
        return f"{rate:.2f}% (based on {opportunities} opportunities at {sampling_rate}% sampling rate)"
    display_rate_formatted.short_description = 'Display Rate (Today)'
    
    def impressions_today_count(self, obj):
        """Get the number of impressions for today"""
        return obj.impressions_today
    impressions_today_count.short_description = 'Impressions (Today)'

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
        
        # Get display rate data
        today = timezone.now().date()
        opportunities = AdOpportunity.objects.filter(campaign=campaign, timestamp__date=today).count()
        shown = AdOpportunity.objects.filter(campaign=campaign, timestamp__date=today, was_shown=True).count()
        display_rate = (shown / opportunities * 100) if opportunities > 0 else 0
        
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
            'display_rate': round(display_rate, 2),
            'sampled_opportunities': opportunities,
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


@admin.register(AdOpportunity)
class AdOpportunityAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'placement', 'was_shown', 'timestamp', 'device_type', 'country')
    list_filter = ('was_shown', 'timestamp', 'campaign', 'placement', 'device_type', 'country')
    search_fields = ('campaign__name', 'placement__name', 'request_id')
    readonly_fields = ('timestamp',)
    fieldsets = (
        (None, {
            'fields': ('campaign', 'placement', 'was_shown', 'request_id')
        }),
        ('Device Information', {
            'fields': ('device_type', 'os', 'country')
        }),
        ('Metadata', {
            'fields': ('timestamp',)
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


@admin.register(DailySpending)
class DailySpendingAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'date', 'amount_spent', 'remaining_budget_display', 'budget_exceeded', 'percentage_spent')
    list_filter = ('date', 'budget_exceeded', 'campaign')
    search_fields = ('campaign__name',)
    readonly_fields = ('created_at', 'updated_at', 'remaining_budget_display', 'percentage_spent')
    fieldsets = (
        ('Campaign Info', {
            'fields': ('campaign', 'date')
        }),
        ('Budget Status', {
            'fields': ('amount_spent', 'remaining_budget_display', 'percentage_spent', 'budget_exceeded')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def remaining_budget_display(self, obj):
        """Display remaining budget"""
        return f"${obj.remaining_budget:.2f}"
    remaining_budget_display.short_description = 'Remaining Budget'
    
    def percentage_spent(self, obj):
        """Show percentage of daily budget spent"""
        if obj.campaign.daily_budget > 0:
            percentage = (obj.amount_spent / obj.campaign.daily_budget) * 100
            if percentage >= 90:
                color = "red"
            elif percentage >= 70:
                color = "orange"
            else:
                color = "green"
            return mark_safe(f'<span style="color: {color}; font-weight: bold;">{percentage:.1f}%</span>')
        return "N/A"
    percentage_spent.short_description = 'Budget Usage' 