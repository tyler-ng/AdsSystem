from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal

from apps.advertising.models import Campaign, DailySpending


class Command(BaseCommand):
    help = 'Test different budget exceeded actions on campaigns'

    def handle(self, *args, **options):
        self.stdout.write('Setting up different budget exceeded actions...')
        
        # Get campaigns and assign different budget exceeded actions
        campaigns = Campaign.objects.filter(status='active')
        
        if len(campaigns) < 1:
            self.stdout.write(
                self.style.WARNING('Need at least 1 active campaign. Run create_sample_data first.')
            )
            return
        
        actions = [
            ('pause_day', 'Pause for the day'),
            ('pause_campaign', 'Pause entire campaign'),
            ('continue_limited', 'Continue with limited frequency'),
            ('stop_immediately', 'Stop serving ads immediately'),
            ('email_notify', 'Email notification only'),
        ]
        
        # Assign different actions to campaigns (cycle through if we have fewer campaigns than actions)
        for i, campaign in enumerate(campaigns):
            action_code, action_name = actions[i % len(actions)]
            
            # Update campaign configuration
            campaign.budget_exceeded_action = action_code
            if action_code == 'continue_limited':
                campaign.budget_exceeded_frequency_cap = 2  # 2 ads per user max
            campaign.save()
            
            self.stdout.write(f'Set {campaign.name} to action: {action_name}')
        
        self.stdout.write('\nSimulating budget exceeded scenarios...')
        
        today = timezone.now().date()
        
        for campaign in campaigns:
            # Exceed budget by 20%
            exceeded_amount = campaign.daily_budget * Decimal('1.2')
            
            # Create or update daily spending
            daily_spending, created = DailySpending.objects.get_or_create(
                campaign=campaign,
                date=today,
                defaults={
                    'amount_spent': Decimal('0.00'),
                    'budget_exceeded': False
                }
            )
            
            # Set spending to exceed budget
            daily_spending.amount_spent = exceeded_amount
            daily_spending.save()
            
            # Trigger budget exceeded handling
            campaign._handle_budget_exceeded(daily_spending)
            
            # Refresh campaign from database to check status changes
            campaign.refresh_from_db()
            
            # Test ad serving capability
            can_show = campaign.can_show_ad()
            
            self.stdout.write(
                f'\n{campaign.name}:'
                f'\n  - Action: {campaign.get_budget_exceeded_action_display()}'
                f'\n  - Budget: ${campaign.daily_budget}, Spent: ${exceeded_amount:.2f}'
                f'\n  - Campaign Status: {campaign.status}'
                f'\n  - Can Show Ads: {"Yes" if can_show else "No"}'
                f'\n  - Is Paused for Day: {"Yes" if campaign.is_paused_for_day() else "No"}'
            )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write('BUDGET EXCEEDED ACTION SUMMARY:')
        self.stdout.write('='*60)
        
        for action_code, action_name in actions:
            self.stdout.write(f'\n{action_name} ({action_code}):')
            if action_code == 'pause_day':
                self.stdout.write('  - Stops ads for rest of day only')
                self.stdout.write('  - Campaign remains active')
                self.stdout.write('  - Resets automatically next day')
            elif action_code == 'pause_campaign':
                self.stdout.write('  - Pauses entire campaign')
                self.stdout.write('  - Requires manual reactivation')
                self.stdout.write('  - Sends notification to advertiser')
            elif action_code == 'continue_limited':
                self.stdout.write('  - Continues serving ads with reduced frequency')
                self.stdout.write('  - Uses frequency cap setting')
                self.stdout.write('  - Good for high-value campaigns')
            elif action_code == 'stop_immediately':
                self.stdout.write('  - Stops ads immediately for the day')
                self.stdout.write('  - Campaign stays active for next day')
                self.stdout.write('  - More conservative than pause_day')
            elif action_code == 'email_notify':
                self.stdout.write('  - Continues serving ads normally')
                self.stdout.write('  - Sends notification only')
                self.stdout.write('  - Useful for monitoring high-value campaigns')
        
        self.stdout.write(
            self.style.SUCCESS('\nSuccessfully configured different budget exceeded actions!')
        ) 