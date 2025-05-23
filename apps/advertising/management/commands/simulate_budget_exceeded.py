from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random

from apps.advertising.models import Campaign, DailySpending


class Command(BaseCommand):
    help = 'Simulate budget exceeded scenarios for demonstration'

    def handle(self, *args, **options):
        self.stdout.write('Simulating budget exceeded scenarios...')
        
        # Get some active campaigns
        campaigns = Campaign.objects.filter(status='active')[:2]
        
        today = timezone.now().date()
        
        for campaign in campaigns:
            # Set today's spending to exceed the daily budget
            daily_spending, created = DailySpending.objects.get_or_create(
                campaign=campaign,
                date=today,
                defaults={
                    'amount_spent': Decimal('0.00'),
                    'budget_exceeded': False
                }
            )
            
            # Exceed the budget by 10-30%
            excess_factor = Decimal(str(random.uniform(1.1, 1.3)))
            exceeded_amount = campaign.daily_budget * excess_factor
            
            daily_spending.amount_spent = exceeded_amount
            daily_spending.budget_exceeded = True
            daily_spending.save()
            
            # Pause the campaign for the day
            campaign.pause_for_day()
            
            self.stdout.write(
                f'Set {campaign.name} spending to ${exceeded_amount:.2f} '
                f'(budget: ${campaign.daily_budget}) - EXCEEDED & PAUSED'
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully simulated budget exceeded scenarios!')
        ) 