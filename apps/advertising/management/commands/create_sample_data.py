from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

from apps.advertising.models import (
    Campaign, Placement, Creative, Target, 
    DailySpending, AdImpression, AdClick, AdOpportunity
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample data for the advertising system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before creating new sample data',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing data...')
            self.reset_data()

        self.stdout.write('Creating sample data...')
        
        # Create sample users (advertisers)
        advertisers = self.create_advertisers()
        
        # Create sample placements
        placements = self.create_placements()
        
        # Create sample campaigns
        campaigns = self.create_campaigns(advertisers)
        
        # Create sample targets for campaigns
        self.create_targets(campaigns)
        
        # Create sample creatives
        creatives = self.create_creatives(campaigns, placements)
        
        # Create sample daily spending records
        self.create_daily_spending(campaigns)
        
        # Create sample impressions and clicks
        self.create_impressions_and_clicks(creatives)
        
        # Create sample ad opportunities
        self.create_ad_opportunities(campaigns, placements)
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )

    def reset_data(self):
        """Reset all advertising data"""
        AdClick.objects.all().delete()
        AdImpression.objects.all().delete()
        AdOpportunity.objects.all().delete()
        DailySpending.objects.all().delete()
        Creative.objects.all().delete()
        Target.objects.all().delete()
        Campaign.objects.all().delete()
        Placement.objects.all().delete()
        # Don't delete users as they might be used elsewhere

    def create_advertisers(self):
        """Create sample advertiser users"""
        advertisers = []
        advertiser_data = [
            {'username': 'nike_ads', 'email': 'ads@nike.com', 'first_name': 'Nike', 'last_name': 'Marketing'},
            {'username': 'coca_cola', 'email': 'marketing@coca-cola.com', 'first_name': 'Coca Cola', 'last_name': 'Team'},
            {'username': 'apple_ads', 'email': 'ads@apple.com', 'first_name': 'Apple', 'last_name': 'Advertising'},
            {'username': 'amazon_promo', 'email': 'promo@amazon.com', 'first_name': 'Amazon', 'last_name': 'Promotions'},
            {'username': 'uber_marketing', 'email': 'marketing@uber.com', 'first_name': 'Uber', 'last_name': 'Marketing'},
        ]
        
        for data in advertiser_data:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                }
            )
            advertisers.append(user)
            if created:
                self.stdout.write(f'Created advertiser: {user.username}')
        
        return advertisers

    def create_placements(self):
        """Create sample ad placements"""
        placement_data = [
            {'name': 'Mobile Banner Top', 'code': 'mobile_banner_top', 'width': 320, 'height': 50},
            {'name': 'Mobile Banner Bottom', 'code': 'mobile_banner_bottom', 'width': 320, 'height': 50},
            {'name': 'Tablet Banner', 'code': 'tablet_banner', 'width': 728, 'height': 90},
            {'name': 'Interstitial Mobile', 'code': 'interstitial_mobile', 'width': 320, 'height': 480},
            {'name': 'Native Feed', 'code': 'native_feed', 'width': 300, 'height': 250},
            {'name': 'Video Player', 'code': 'video_player', 'width': 640, 'height': 360},
        ]
        
        placements = []
        for data in placement_data:
            placement, created = Placement.objects.get_or_create(
                code=data['code'],
                defaults={
                    'name': data['name'],
                    'recommended_width': data['width'],
                    'recommended_height': data['height'],
                    'description': f"Placement for {data['name']}"
                }
            )
            placements.append(placement)
            if created:
                self.stdout.write(f'Created placement: {placement.name}')
        
        return placements

    def create_campaigns(self, advertisers):
        """Create sample campaigns with various statuses and budgets"""
        campaigns = []
        campaign_data = [
            {
                'name': 'Nike Summer Sale 2025',
                'company_name': 'Nike Inc.',
                'advertiser': advertisers[0],
                'status': 'active',
                'daily_budget': Decimal('150.00'),
                'total_budget': Decimal('5000.00'),
                'description': 'Promoting summer athletic wear collection'
            },
            {
                'name': 'Coca Cola Refresh Campaign',
                'company_name': 'The Coca-Cola Company',
                'advertiser': advertisers[1],
                'status': 'active',
                'daily_budget': Decimal('200.00'),
                'total_budget': Decimal('8000.00'),
                'description': 'Refreshing summer beverage campaign'
            },
            {
                'name': 'iPhone 16 Launch',
                'company_name': 'Apple Inc.',
                'advertiser': advertisers[2],
                'status': 'active',
                'daily_budget': Decimal('500.00'),
                'total_budget': Decimal('20000.00'),
                'description': 'New iPhone launch campaign'
            },
            {
                'name': 'Amazon Prime Day Preview',
                'company_name': 'Amazon.com Inc.',
                'advertiser': advertisers[3],
                'status': 'paused',
                'daily_budget': Decimal('300.00'),
                'total_budget': Decimal('10000.00'),
                'description': 'Early access to Prime Day deals'
            },
            {
                'name': 'Uber Eats Weekend Deals',
                'company_name': 'Uber Technologies Inc.',
                'advertiser': advertisers[4],
                'status': 'active',
                'daily_budget': Decimal('100.00'),
                'total_budget': Decimal('2000.00'),
                'description': 'Weekend food delivery promotions'
            },
            {
                'name': 'Nike Holiday Collection',
                'company_name': 'Nike Inc.',
                'advertiser': advertisers[0],
                'status': 'draft',
                'daily_budget': Decimal('250.00'),
                'total_budget': Decimal('7500.00'),
                'description': 'Holiday season athletic collection'
            }
        ]
        
        for data in campaign_data:
            start_date = timezone.now() - timedelta(days=random.randint(1, 30))
            end_date = start_date + timedelta(days=random.randint(30, 90))
            
            campaign = Campaign.objects.create(
                name=data['name'],
                company_name=data['company_name'],
                advertiser=data['advertiser'],
                status=data['status'],
                daily_budget=data['daily_budget'],
                total_budget=data['total_budget'],
                description=data['description'],
                start_date=start_date,
                end_date=end_date,
                opportunity_sampling_rate=random.uniform(3.0, 10.0)
            )
            campaigns.append(campaign)
            self.stdout.write(f'Created campaign: {campaign.name}')
        
        return campaigns

    def create_targets(self, campaigns):
        """Create targeting criteria for campaigns"""
        countries_options = [
            ['US', 'CA'],
            ['US', 'CA', 'GB'],
            ['US'],
            ['US', 'CA', 'GB', 'AU'],
            ['US', 'CA', 'MX']
        ]
        
        interests_options = [
            ['sports', 'fitness'],
            ['food', 'beverages'],
            ['technology', 'mobile'],
            ['shopping', 'deals'],
            ['food', 'delivery'],
            ['sports', 'apparel']
        ]
        
        for i, campaign in enumerate(campaigns):
            target = Target.objects.create(
                campaign=campaign,
                os_android=random.choice([True, False]) or True,
                os_ios=random.choice([True, False]) or True,
                gender=random.choice(['all', 'male', 'female']),
                age_min=random.choice([18, 21, 25]),
                age_max=random.choice([45, 55, 65]),
                countries=countries_options[i % len(countries_options)],
                interests=interests_options[i % len(interests_options)]
            )
            self.stdout.write(f'Created target for: {campaign.name}')

    def create_creatives(self, campaigns, placements):
        """Create sample ad creatives"""
        creatives = []
        
        creative_templates = [
            {
                'title': 'Summer Sale - Up to 50% Off!',
                'description': 'Don\'t miss our biggest summer sale',
                'cta': 'Shop Now',
                'type': 'banner'
            },
            {
                'title': 'Refresh Your Day',
                'description': 'Ice cold beverages delivered fresh',
                'cta': 'Order Now',
                'type': 'banner'
            },
            {
                'title': 'iPhone 16 Available Now',
                'description': 'The most advanced iPhone yet',
                'cta': 'Learn More',
                'type': 'interstitial'
            },
            {
                'title': 'Prime Day Deals',
                'description': 'Exclusive deals for Prime members',
                'cta': 'Shop Deals',
                'type': 'native'
            },
            {
                'title': 'Weekend Food Deals',
                'description': 'Free delivery on orders over $20',
                'cta': 'Order Food',
                'type': 'banner'
            }
        ]
        
        for i, campaign in enumerate(campaigns[:5]):  # Create creatives for first 5 campaigns
            template = creative_templates[i % len(creative_templates)]
            placement = random.choice(placements)
            
            creative = Creative.objects.create(
                campaign=campaign,
                placement=placement,
                name=f"{campaign.name} - {template['type'].title()}",
                type=template['type'],
                title=template['title'],
                description=template['description'],
                call_to_action=template['cta'],
                destination_url=f"https://example.com/{campaign.company_name.lower().replace(' ', '')}",
                width=placement.recommended_width,
                height=placement.recommended_height,
                is_active=campaign.status == 'active'
            )
            creatives.append(creative)
            self.stdout.write(f'Created creative: {creative.name}')
        
        return creatives

    def create_daily_spending(self, campaigns):
        """Create sample daily spending records"""
        today = timezone.now().date()
        
        for campaign in campaigns:
            if campaign.status == 'active':
                # Create spending for the last 7 days
                for days_ago in range(7):
                    date = today - timedelta(days=days_ago)
                    
                    # Generate realistic spending amounts
                    if days_ago == 0:  # Today
                        max_spent = campaign.daily_budget * Decimal('0.8')  # 80% of daily budget
                    else:
                        max_spent = campaign.daily_budget * Decimal(random.uniform(0.3, 1.1))
                    
                    amount_spent = Decimal(str(round(random.uniform(0, float(max_spent)), 2)))
                    budget_exceeded = amount_spent >= campaign.daily_budget
                    
                    daily_spending = DailySpending.objects.create(
                        campaign=campaign,
                        date=date,
                        amount_spent=amount_spent,
                        budget_exceeded=budget_exceeded
                    )
                    
                    if days_ago == 0:  # Only print today's spending
                        self.stdout.write(
                            f'Daily spending for {campaign.name}: ${amount_spent} '
                            f'({"EXCEEDED" if budget_exceeded else "WITHIN"} budget)'
                        )

    def create_impressions_and_clicks(self, creatives):
        """Create sample impression and click data"""
        countries = ['US', 'CA', 'GB', 'AU']
        devices = ['phone', 'tablet']
        os_list = ['android', 'ios']
        
        for creative in creatives:
            # Create impressions for the last 3 days
            for days_ago in range(3):
                impressions_count = random.randint(50, 500)
                
                for _ in range(impressions_count):
                    timestamp = timezone.now() - timedelta(
                        days=days_ago,
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                    
                    impression = AdImpression.objects.create(
                        creative=creative,
                        campaign=creative.campaign,
                        device_type=random.choice(devices),
                        os=random.choice(os_list),
                        country=random.choice(countries),
                        app_id=f"com.example.app{random.randint(1, 5)}",
                        timestamp=timestamp
                    )
                    
                    # Create clicks for some impressions (realistic CTR: 2-5%)
                    if random.random() < 0.035:  # 3.5% CTR
                        AdClick.objects.create(
                            impression=impression,
                            creative=creative,
                            campaign=creative.campaign,
                            timestamp=timestamp + timedelta(seconds=random.randint(1, 30))
                        )
            
            impressions = creative.impressions.count()
            clicks = creative.clicks.count()
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            self.stdout.write(
                f'{creative.name}: {impressions} impressions, {clicks} clicks ({ctr:.2f}% CTR)'
            )

    def create_ad_opportunities(self, campaigns, placements):
        """Create sample ad opportunity records"""
        for campaign in campaigns[:3]:  # Only for first 3 campaigns
            placement = random.choice(placements)
            
            # Create opportunities for the last 2 days
            for days_ago in range(2):
                opportunities_count = random.randint(100, 1000)
                shown_count = int(opportunities_count * random.uniform(0.1, 0.4))  # 10-40% display rate
                
                for i in range(opportunities_count):
                    timestamp = timezone.now() - timedelta(
                        days=days_ago,
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                    
                    AdOpportunity.objects.create(
                        campaign=campaign,
                        placement=placement,
                        was_shown=i < shown_count,
                        request_id=f"req_{random.randint(100000, 999999)}",
                        timestamp=timestamp,
                        device_type=random.choice(['phone', 'tablet']),
                        os=random.choice(['android', 'ios']),
                        country=random.choice(['US', 'CA', 'GB'])
                    )
            
            display_rate = campaign.display_rate_today
            self.stdout.write(f'{campaign.name} display rate: {display_rate:.2f}%') 