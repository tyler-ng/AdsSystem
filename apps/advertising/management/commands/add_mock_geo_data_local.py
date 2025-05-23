import random
import uuid
import os
import sys
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
from apps.advertising.models import Campaign, Creative, AdImpression

User = get_user_model()

# Countries represented by their 2-letter ISO codes and approximate impression counts
COUNTRIES_DATA = [
    ('US', 2500),  # United States
    ('GB', 1800),  # United Kingdom
    ('CA', 1200),  # Canada
    ('AU', 950),   # Australia
    ('DE', 750),   # Germany
    ('FR', 680),   # France
    ('JP', 520),   # Japan
    ('IN', 480),   # India
    ('BR', 410),   # Brazil
    ('MX', 350),   # Mexico
    ('ES', 320),   # Spain
    ('IT', 290),   # Italy
    ('NL', 240),   # Netherlands
    ('SE', 210),   # Sweden
    ('SG', 180),   # Singapore
    ('KR', 150),   # South Korea
    ('RU', 130),   # Russia
    ('AE', 110),   # United Arab Emirates
    ('ZA', 90),    # South Africa
    ('AR', 70),    # Argentina
]

# Device types for mock data - mobile only
DEVICE_TYPES = ['smartphone']

# OS types for mock data - mobile OS only
OS_TYPES = ['iOS', 'Android']


class Command(BaseCommand):
    help = 'Adds mock geographic distribution data to test campaigns (for local development)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--campaign',
            help='Campaign name to add data for (will use "Test Campaign" if not provided)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing impression data before adding mock data',
        )

    def handle(self, *args, **options):
        # Modify database settings directly (before any database operations)
        settings.DATABASES['default']['HOST'] = 'localhost'
        settings.DATABASES['default']['PORT'] = '5433'
        
        self.stdout.write(self.style.SUCCESS(f"Using database at {settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}"))
        
        # Get or set default campaign name
        campaign_name = options.get('campaign')
        if not campaign_name:
            campaign_name = "Test Campaign"
        
        should_reset = options.get('reset', False)
        
        # Find the campaign or create it if it doesn't exist
        try:
            campaign = Campaign.objects.get(name=campaign_name)
            self.stdout.write(self.style.SUCCESS(f'Found campaign: {campaign_name}'))
        except Campaign.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'Campaign "{campaign_name}" not found. Creating it...'))
            
            # Get the first admin user or create one if none exists
            try:
                admin_user = User.objects.filter(is_staff=True).first()
                if not admin_user:
                    admin_user = User.objects.create_superuser(
                        username='admin',
                        email='admin@example.com',
                        password='adminpassword'
                    )
                    self.stdout.write(self.style.SUCCESS('Created admin user'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to get or create admin user: {e}'))
                return
                
            # Create the campaign
            campaign = Campaign.objects.create(
                name=campaign_name,
                company_name='Acme Corporation',
                advertiser=admin_user,
                status='active',
                start_date=timezone.now() - timezone.timedelta(days=30),
                end_date=timezone.now() + timezone.timedelta(days=60),
                daily_budget=1000.00,
                total_budget=30000.00,
                description='A test campaign with mock geographic data'
            )
            self.stdout.write(self.style.SUCCESS(f'Created campaign: {campaign_name}'))
            
            # Create a sample creative for the campaign
            creative = Creative.objects.create(
                campaign=campaign,
                name='Test Banner',
                type='banner',
                title='Amazing Product',
                description='Check out our amazing product',
                call_to_action='Learn More',
                destination_url='https://example.com/product',
                width=300,
                height=250,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created creative: {creative.name}'))
            
        # Get a creative from the campaign or create one if none exists
        creative = Creative.objects.filter(campaign=campaign).first()
        if not creative:
            creative = Creative.objects.create(
                campaign=campaign,
                name='Test Banner',
                type='banner',
                title='Amazing Product',
                description='Check out our amazing product',
                call_to_action='Learn More',
                destination_url='https://example.com/product',
                width=300,
                height=250,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created creative: {creative.name}'))
        
        # Reset data if specified
        if should_reset:
            count = AdImpression.objects.filter(campaign=campaign).count()
            AdImpression.objects.filter(campaign=campaign).delete()
            self.stdout.write(self.style.WARNING(f'Deleted {count} existing impression records for campaign: {campaign_name}'))
            
        # Add mock data for geographic distribution
        impressions_to_create = []
        total_count = 0
        
        for country_code, count in COUNTRIES_DATA:
            self.stdout.write(f"Adding {count} impressions for {country_code}...")
            for _ in range(count):
                impression = AdImpression(
                    id=uuid.uuid4(),
                    creative=creative,
                    campaign=campaign,
                    country=country_code,
                    device_type=random.choice(DEVICE_TYPES),
                    os=random.choice(OS_TYPES),
                    os_version=f'{random.randint(10, 15)}.{random.randint(0, 9)}',
                    ip_address=f'{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}',
                    user_agent='Mozilla/5.0 (Mock User Agent)',
                    timestamp=timezone.now() - timezone.timedelta(
                        days=random.randint(0, 30),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                )
                impressions_to_create.append(impression)
                total_count += 1
                
                # Bulk create in batches of 1000 to avoid memory issues
                if len(impressions_to_create) >= 1000:
                    AdImpression.objects.bulk_create(impressions_to_create)
                    self.stdout.write(self.style.SUCCESS(f"Created 1000 impressions..."))
                    impressions_to_create = []
                    
        # Create any remaining impressions
        if impressions_to_create:
            AdImpression.objects.bulk_create(impressions_to_create)
            self.stdout.write(self.style.SUCCESS(f"Created {len(impressions_to_create)} impressions..."))
            
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully added {total_count} mock geographic impressions for {len(COUNTRIES_DATA)} countries'
            )
        ) 