from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils import timezone
from decimal import Decimal


class Campaign(models.Model):
    """Model for advertising campaigns"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('paused', _('Paused')),
        ('completed', _('Completed')),
        ('archived', _('Archived')),
    )
    
    BUDGET_EXCEEDED_ACTIONS = (
        ('pause_day', _('Pause for the day')),
        ('pause_campaign', _('Pause entire campaign')),
        ('continue_limited', _('Continue with limited frequency')),
        ('stop_immediately', _('Stop serving ads immediately')),
        ('email_notify', _('Email notification only')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Campaign Name'), max_length=255)
    company_name = models.CharField(_('Company Name'), max_length=255, blank=False, help_text=_('The company this campaign belongs to'))
    advertiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Budget exceeded configuration
    budget_exceeded_action = models.CharField(
        _('Budget Exceeded Action'), 
        max_length=20, 
        choices=BUDGET_EXCEEDED_ACTIONS, 
        default='pause_day',
        help_text=_('What to do when daily budget is exceeded')
    )
    
    # Opportunity sampling rate for tracking
    opportunity_sampling_rate = models.FloatField(
        _('Opportunity Sampling Rate (%)'), 
        default=5.0,
        validators=[MinValueValidator(0.1), MaxValueValidator(100.0)],
        help_text=_('Percentage of traffic to sample for opportunity tracking')
    )
    
    # Optional: Reduced frequency when budget exceeded (for continue_limited option)
    budget_exceeded_frequency_cap = models.PositiveIntegerField(
        _('Budget Exceeded Frequency Cap'),
        default=1,
        help_text=_('Maximum ads per user when budget exceeded (for continue_limited action)')
    )
    
    start_date = models.DateTimeField(_('Start Date'))
    end_date = models.DateTimeField(_('End Date'), null=True, blank=True)
    daily_budget = models.DecimalField(_('Daily Budget'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_budget = models.DecimalField(_('Total Budget'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField(_('Description'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Campaign')
        verbose_name_plural = _('Campaigns')
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        """Check if campaign is currently active"""
        now = timezone.now()
        if self.status != 'active':
            return False
        if now < self.start_date:
            return False
        if self.end_date and now > self.end_date:
            return False
        return True
        
    @property
    def impressions_today(self):
        """Get the number of impressions for today"""
        today = timezone.now().date()
        return self.impressions.filter(
            timestamp__date=today
        ).count()
        
    @property
    def display_rate_today(self):
        """Calculate display rate based on sampled opportunities"""
        today = timezone.now().date()
        opportunities = self.opportunities.filter(timestamp__date=today).count()
        shown = self.opportunities.filter(timestamp__date=today, was_shown=True).count()
        
        if opportunities == 0:
            return 0.0
        
        return (shown / opportunities) * 100.0

    def get_daily_spending(self, date=None):
        """Get total spending for a specific date (today by default)"""
        if date is None:
            date = timezone.now().date()
        
        daily_spending, created = DailySpending.objects.get_or_create(
            campaign=self,
            date=date,
            defaults={'amount_spent': Decimal('0.00')}
        )
        return daily_spending.amount_spent

    def check_daily_budget_available(self, amount=None, date=None):
        """Check if campaign has budget available for today"""
        if date is None:
            date = timezone.now().date()
        
        current_spending = self.get_daily_spending(date)
        
        if amount is None:
            # Just check if any budget is available
            return current_spending < self.daily_budget
        else:
            # Check if specific amount can be spent
            return (current_spending + Decimal(str(amount))) <= self.daily_budget

    def can_show_ad(self, estimated_cost=Decimal('0.01')):
        """Check if campaign can show an ad based on daily budget and configuration"""
        if not self.is_active:
            return False
        
        # Check if we're within daily budget
        if not self.check_daily_budget_available(estimated_cost):
            # Budget exceeded - check the configured action
            return self._handle_budget_exceeded_check()
        
        return True

    def _handle_budget_exceeded_check(self):
        """Handle different budget exceeded actions for ad serving"""
        if self.budget_exceeded_action == 'pause_day':
            return False  # Don't show ads for rest of day
        elif self.budget_exceeded_action == 'pause_campaign':
            return False  # Don't show ads (campaign should be paused)
        elif self.budget_exceeded_action == 'continue_limited':
            # Could implement frequency capping logic here
            # For now, allow with reduced probability
            import random
            return random.random() < 0.1  # 10% chance to show ad
        elif self.budget_exceeded_action == 'stop_immediately':
            return False  # Stop immediately
        elif self.budget_exceeded_action == 'email_notify':
            return True  # Continue showing ads but notify
        
        return False  # Default to not showing

    def record_spending(self, amount, date=None):
        """Record spending for the campaign and handle budget exceeded actions"""
        if date is None:
            date = timezone.now().date()
        
        daily_spending, created = DailySpending.objects.get_or_create(
            campaign=self,
            date=date,
            defaults={'amount_spent': Decimal('0.00')}
        )
        
        daily_spending.amount_spent += Decimal(str(amount))
        daily_spending.save()
        
        # Check if daily budget exceeded and handle according to configuration
        if daily_spending.amount_spent >= self.daily_budget:
            self._handle_budget_exceeded(daily_spending)
        
        return daily_spending

    def _handle_budget_exceeded(self, daily_spending):
        """Handle different budget exceeded actions"""
        daily_spending.budget_exceeded = True
        daily_spending.save()
        
        if self.budget_exceeded_action == 'pause_day':
            # Mark as paused for the day (existing behavior)
            pass  # budget_exceeded flag is already set
            
        elif self.budget_exceeded_action == 'pause_campaign':
            # Pause the entire campaign
            self.status = 'paused'
            self.save()
            self._send_budget_notification('Campaign paused due to budget exceeded')
            
        elif self.budget_exceeded_action == 'continue_limited':
            # Continue with limited frequency (handled in can_show_ad)
            self._send_budget_notification('Budget exceeded - serving ads with limited frequency')
            
        elif self.budget_exceeded_action == 'stop_immediately':
            # Stop serving immediately but don't pause campaign
            self._send_budget_notification('Budget exceeded - ads stopped for today')
            
        elif self.budget_exceeded_action == 'email_notify':
            # Just send notification but continue
            self._send_budget_notification('Daily budget exceeded but campaign continues')

    def _send_budget_notification(self, message):
        """Send budget exceeded notification (placeholder for actual implementation)"""
        # TODO: Implement actual email notification
        print(f"BUDGET NOTIFICATION for {self.name}: {message}")
        
        # You could implement:
        # - Email to advertiser
        # - Slack notification  
        # - SMS alert
        # - Dashboard notification
        pass

    def pause_for_day(self):
        """Pause campaign for the rest of the day due to budget limit"""
        # You could implement a more sophisticated pause mechanism here
        # For now, we'll just mark it in the daily spending record
        today = timezone.now().date()
        daily_spending, created = DailySpending.objects.get_or_create(
            campaign=self,
            date=today,
            defaults={'amount_spent': Decimal('0.00')}
        )
        daily_spending.budget_exceeded = True
        daily_spending.save()

    def is_paused_for_day(self, date=None):
        """Check if campaign is paused for today due to budget"""
        if date is None:
            date = timezone.now().date()
        
        try:
            daily_spending = DailySpending.objects.get(campaign=self, date=date)
            return daily_spending.budget_exceeded
        except DailySpending.DoesNotExist:
            return False


class DailySpending(models.Model):
    """Model to track daily spending for campaigns"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='daily_spendings')
    date = models.DateField(_('Date'))
    amount_spent = models.DecimalField(_('Amount Spent'), max_digits=10, decimal_places=2, default=0)
    budget_exceeded = models.BooleanField(_('Budget Exceeded'), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Daily Spending')
        verbose_name_plural = _('Daily Spendings')
        unique_together = ['campaign', 'date']
        ordering = ['-date']

    def __str__(self):
        return f"{self.campaign.name} - {self.date}: ${self.amount_spent}"

    @property
    def remaining_budget(self):
        """Calculate remaining daily budget"""
        return max(self.campaign.daily_budget - self.amount_spent, Decimal('0.00'))


class Placement(models.Model):
    """Model for ad placement locations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Placement Name'), max_length=255)
    code = models.CharField(_('Placement Code'), max_length=100, unique=True, 
                          help_text=_('Unique code for this placement'))
    description = models.TextField(_('Description'), blank=True)
    recommended_width = models.PositiveIntegerField(_('Recommended Width'), null=True, blank=True)
    recommended_height = models.PositiveIntegerField(_('Recommended Height'), null=True, blank=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Placement')
        verbose_name_plural = _('Placements')
        ordering = ['name']

    def __str__(self):
        return self.name


class Creative(models.Model):
    """Model for ad creatives"""
    TYPE_CHOICES = (
        ('banner', _('Banner')),
        ('interstitial', _('Interstitial')),
        ('native', _('Native')),
        ('video', _('Video')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='creatives')
    placement = models.ForeignKey(Placement, on_delete=models.SET_NULL, related_name='creatives', 
                                null=True, blank=True, 
                                help_text=_('The placement location for this creative'))
    name = models.CharField(_('Creative Name'), max_length=255)
    type = models.CharField(_('Creative Type'), max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(_('Title'), max_length=255, blank=True)
    description = models.TextField(_('Description'), blank=True)
    image = models.ImageField(_('Image'), upload_to='ad_creatives/', null=True, blank=True)
    video = models.FileField(_('Video'), upload_to='ad_videos/', null=True, blank=True)
    call_to_action = models.CharField(_('Call to Action'), max_length=50, blank=True)
    destination_url = models.URLField(_('Destination URL'))
    width = models.PositiveIntegerField(_('Width'), null=True, blank=True)
    height = models.PositiveIntegerField(_('Height'), null=True, blank=True)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Creative')
        verbose_name_plural = _('Creatives')
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Target(models.Model):
    """Model for ad targeting criteria"""
    GENDER_CHOICES = (
        ('all', _('All')),
        ('male', _('Male')),
        ('female', _('Female')),
        ('other', _('Other')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='targets')
    
    # Device targeting
    os_android = models.BooleanField(_('Android'), default=True)
    os_ios = models.BooleanField(_('iOS'), default=True)
    os_version_min = models.CharField(_('Minimum OS Version'), max_length=20, blank=True)
    os_version_max = models.CharField(_('Maximum OS Version'), max_length=20, blank=True)
    
    # Demographic targeting
    gender = models.CharField(_('Gender'), max_length=10, choices=GENDER_CHOICES, default='all')
    age_min = models.PositiveIntegerField(_('Minimum Age'), null=True, blank=True)
    age_max = models.PositiveIntegerField(_('Maximum Age'), null=True, blank=True)
    
    # Location targeting
    countries = models.JSONField(_('Countries'), default=list, blank=True)
    regions = models.JSONField(_('Regions'), default=list, blank=True)
    cities = models.JSONField(_('Cities'), default=list, blank=True)
    
    # Interest targeting
    interests = models.JSONField(_('Interests'), default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Target')
        verbose_name_plural = _('Targets')

    def __str__(self):
        return f"Target for {self.campaign.name}"


# Model for sampled ad opportunities (for display rate calculation)
class AdOpportunity(models.Model):
    """Model for tracking sampled ad display opportunities"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='opportunities')
    placement = models.ForeignKey(Placement, on_delete=models.CASCADE, related_name='opportunities')
    was_shown = models.BooleanField(_('Was Ad Shown'), default=False, 
                                  help_text=_('Whether this campaign was selected for display'))
    request_id = models.CharField(_('Request ID'), max_length=100, 
                               help_text=_('Unique identifier for the ad request'))
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional context data
    device_type = models.CharField(_('Device Type'), max_length=50, blank=True)
    os = models.CharField(_('Operating System'), max_length=50, blank=True)
    country = models.CharField(_('Country'), max_length=2, blank=True)
    
    class Meta:
        verbose_name = _('Ad Opportunity')
        verbose_name_plural = _('Ad Opportunities')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['campaign', 'timestamp']),
            models.Index(fields=['placement', 'timestamp']),
            models.Index(fields=['request_id']),
        ]


class AdImpression(models.Model):
    """Model for tracking ad impressions"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creative = models.ForeignKey(Creative, on_delete=models.CASCADE, related_name='impressions')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='impressions')
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    device_type = models.CharField(_('Device Type'), max_length=50, blank=True)
    os = models.CharField(_('Operating System'), max_length=50, blank=True)
    os_version = models.CharField(_('OS Version'), max_length=20, blank=True)
    country = models.CharField(_('Country'), max_length=2, blank=True)
    region = models.CharField(_('Region'), max_length=100, blank=True)
    city = models.CharField(_('City'), max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # For mobile app specific data
    app_id = models.CharField(_('App ID'), max_length=255, blank=True)
    app_version = models.CharField(_('App Version'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('Ad Impression')
        verbose_name_plural = _('Ad Impressions')
        ordering = ['-timestamp']


class AdClick(models.Model):
    """Model for tracking ad clicks"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    impression = models.OneToOneField(AdImpression, on_delete=models.CASCADE, related_name='click', null=True, blank=True)
    creative = models.ForeignKey(Creative, on_delete=models.CASCADE, related_name='clicks')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='clicks')
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Ad Click')
        verbose_name_plural = _('Ad Clicks')
        ordering = ['-timestamp'] 