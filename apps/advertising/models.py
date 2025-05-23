from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from django.utils import timezone


class Campaign(models.Model):
    """Model for advertising campaigns"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('paused', _('Paused')),
        ('completed', _('Completed')),
        ('archived', _('Archived')),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Campaign Name'), max_length=255)
    company_name = models.CharField(_('Company Name'), max_length=255, blank=False, help_text=_('The company this campaign belongs to'))
    advertiser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
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