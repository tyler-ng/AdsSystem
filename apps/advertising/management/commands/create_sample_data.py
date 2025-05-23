import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.advertising.models import Campaign, Creative, Target, Placement

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates sample campaigns with placements and creatives for testing'

    def add_arguments(self, parser):
        parser.add_argument('--campaigns', type=int, default=3, help='Number of campaigns to create')
        parser.add_argument('--placements', type=int, default=5, help='Number of placements to create')
        parser.add_argument('--creatives', type=int, default=10, help='Number of creatives to create')

    def handle(self, *args, **options):
        num_campaigns = options['campaigns']
        num_placements = options['placements']
        num_creatives = options['creatives']
        
        # Check if admin user exists, create if not
        try:
            admin_user = User.objects.get(username='admin')
            self.stdout.write(self.style.SUCCESS('Using existing admin user'))
        except User.DoesNotExist:
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='adminpassword'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        # Create sample placements
        self.stdout.write('Creating placements...')
        placements = []
        placement_types = [
            ('Banner Top', 'banner_top', 'Top banner placement', 728, 90),
            ('Banner Bottom', 'banner_bottom', 'Bottom banner placement', 728, 90),
            ('Sidebar', 'sidebar', 'Sidebar placement', 300, 250),
            ('Interstitial', 'interstitial', 'Full screen interstitial', 1080, 1920),
            ('Native Feed', 'native_feed', 'Native ad in feed', 400, 300),
            ('Video Player', 'video_player', 'In-stream video placement', 640, 360),
            ('App Open', 'app_open', 'App open placement', 1080, 1920),
            ('Rewarded', 'rewarded', 'Rewarded ad placement', 1080, 1920),
        ]
        
        # Use predefined placements first, then generate random ones if needed
        for i in range(min(len(placement_types), num_placements)):
            name, code, desc, width, height = placement_types[i]
            placement = Placement.objects.create(
                name=name,
                code=code,
                description=desc,
                recommended_width=width,
                recommended_height=height,
                is_active=True
            )
            placements.append(placement)
            self.stdout.write(f'  - Created placement: {name}')
        
        # Create additional random placements if needed
        for i in range(max(0, num_placements - len(placement_types))):
            idx = len(placement_types) + i
            placement = Placement.objects.create(
                name=f'Custom Placement {idx}',
                code=f'custom_{idx}',
                description=f'Custom placement {idx} description',
                recommended_width=random.choice([300, 320, 728, 1080]),
                recommended_height=random.choice([50, 90, 250, 280, 1920]),
                is_active=True
            )
            placements.append(placement)
            self.stdout.write(f'  - Created placement: Custom Placement {idx}')
        
        # Create sample campaigns
        self.stdout.write('Creating campaigns...')
        campaigns = []
        companies = ['TechCorp', 'FoodDelivery', 'TravelApp', 'FitnessGuru', 'GameStudio', 'FashionBrand']
        statuses = ['draft', 'active', 'paused', 'completed', 'archived']
        
        for i in range(num_campaigns):
            now = timezone.now()
            start_date = now - timedelta(days=random.randint(0, 30))
            end_date = start_date + timedelta(days=random.randint(30, 90))
            
            campaign = Campaign.objects.create(
                name=f'Campaign {i+1} - {random.choice(companies)}',
                company_name=random.choice(companies),
                advertiser=admin_user,
                status=random.choice(statuses),
                start_date=start_date,
                end_date=end_date,
                daily_budget=random.randint(50, 500),
                total_budget=random.randint(1000, 10000),
                description=f'This is a sample campaign {i+1}'
            )
            campaigns.append(campaign)
            self.stdout.write(f'  - Created campaign: {campaign.name}')
            
            # Create targeting for campaign
            Target.objects.create(
                campaign=campaign,
                os_android=random.choice([True, False]),
                os_ios=random.choice([True, False]),
                gender=random.choice(['all', 'male', 'female']),
                age_min=random.choice([None, 18, 25, 30]),
                age_max=random.choice([None, 35, 45, 65]),
                countries=['US', 'CA'] if random.choice([True, False]) else [],
                interests=['games', 'sports', 'technology'] if random.choice([True, False]) else []
            )
        
        # Create sample creatives
        self.stdout.write('Creating creatives...')
        creative_types = ['banner', 'interstitial', 'native', 'video']
        titles = ['Amazing Offer', 'Limited Time Deal', 'New Product', 'Best App', 'Try Now']
        descriptions = [
            'Check out our amazing product!',
            'Limited time offer, act now!',
            'The best app for your needs',
            'Join thousands of satisfied users',
            'Exclusive deal just for you'
        ]
        cta_texts = ['Learn More', 'Download Now', 'Sign Up', 'Get Started', 'Buy Now']
        
        for i in range(num_creatives):
            campaign = random.choice(campaigns)
            placement = random.choice(placements)
            creative_type = random.choice(creative_types)
            
            creative = Creative.objects.create(
                campaign=campaign,
                placement=placement,
                name=f'Creative {i+1} for {campaign.name}',
                type=creative_type,
                title=random.choice(titles),
                description=random.choice(descriptions),
                call_to_action=random.choice(cta_texts),
                destination_url='https://example.com/landing',
                width=placement.recommended_width,
                height=placement.recommended_height,
                is_active=random.choice([True, False])
            )
            self.stdout.write(f'  - Created creative: {creative.name} ({creative.type}) for placement: {placement.name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_campaigns} campaigns, {len(placements)} placements, and {num_creatives} creatives')) 