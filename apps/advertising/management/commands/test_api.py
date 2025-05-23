import json
import requests
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class Command(BaseCommand):
    help = 'Tests the advertising API endpoints including placements'

    def add_arguments(self, parser):
        parser.add_argument('--host', type=str, default='http://localhost:8000', help='API host')

    def handle(self, *args, **options):
        host = options['host']
        
        # Get admin user
        try:
            admin_user = User.objects.get(username='admin')
            self.stdout.write(self.style.SUCCESS('Using existing admin user for API tests'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR('Admin user not found. Please create an admin user first.'))
            return
        
        # Get JWT token for authentication
        refresh = RefreshToken.for_user(admin_user)
        access_token = str(refresh.access_token)
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        # Test endpoints
        self._test_placements_endpoint(host, headers)
        self._test_campaigns_endpoint(host, headers)
        self._test_creatives_endpoint(host, headers)
        
    def _test_placements_endpoint(self, host, headers):
        self.stdout.write('Testing placements API...')
        
        # List placements
        response = requests.get(f'{host}/api/v1/advertising/placements/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.stdout.write(self.style.SUCCESS(f'Successfully fetched {len(data)} placements'))
            
            if len(data) > 0:
                self.stdout.write('Sample placement data:')
                self.stdout.write(json.dumps(data[0], indent=2))
        else:
            self.stdout.write(self.style.ERROR(f'Failed to fetch placements: {response.status_code}'))
            self.stdout.write(response.text)
    
    def _test_campaigns_endpoint(self, host, headers):
        self.stdout.write('Testing campaigns API...')
        
        # List campaigns
        response = requests.get(f'{host}/api/v1/advertising/campaigns/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            self.stdout.write(self.style.SUCCESS(f'Successfully fetched campaigns'))
            
            if 'results' in data and len(data['results']) > 0:
                campaign_id = data['results'][0]['id']
                self.stdout.write(f'Testing campaign detail for ID: {campaign_id}')
                
                # Get campaign detail
                response = requests.get(f'{host}/api/v1/advertising/campaigns/{campaign_id}/', headers=headers)
                if response.status_code == 200:
                    campaign_data = response.json()
                    self.stdout.write(self.style.SUCCESS('Successfully fetched campaign detail'))
                    self.stdout.write(f'Campaign name: {campaign_data["name"]}')
                    
                    # Check if creatives have placement data
                    if 'creatives' in campaign_data and len(campaign_data['creatives']) > 0:
                        creative = campaign_data['creatives'][0]
                        if 'placement_details' in creative:
                            self.stdout.write(self.style.SUCCESS('Creative has placement data'))
                            self.stdout.write(f'Placement: {creative["placement_details"]["name"]}')
                        else:
                            self.stdout.write(self.style.WARNING('Creative does not have placement data'))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to fetch campaign detail: {response.status_code}'))
        else:
            self.stdout.write(self.style.ERROR(f'Failed to fetch campaigns: {response.status_code}'))
    
    def _test_creatives_endpoint(self, host, headers):
        self.stdout.write('Testing creatives API for a campaign...')
        
        # Get first campaign
        response = requests.get(f'{host}/api/v1/advertising/campaigns/', headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                campaign_id = data['results'][0]['id']
                
                # Get creatives for campaign
                response = requests.get(f'{host}/api/v1/advertising/campaigns/{campaign_id}/creatives/', headers=headers)
                if response.status_code == 200:
                    creatives = response.json()
                    self.stdout.write(self.style.SUCCESS(f'Successfully fetched {len(creatives)} creatives for campaign'))
                    
                    if len(creatives) > 0:
                        creative = creatives[0]
                        self.stdout.write(f'Creative name: {creative["name"]}')
                        if 'placement' in creative and creative['placement']:
                            self.stdout.write(self.style.SUCCESS(f'Creative has placement ID: {creative["placement"]}'))
                        if 'placement_details' in creative and creative['placement_details']:
                            self.stdout.write(self.style.SUCCESS(f'Creative has placement details: {creative["placement_details"]["name"]}'))
                else:
                    self.stdout.write(self.style.ERROR(f'Failed to fetch creatives: {response.status_code}')) 