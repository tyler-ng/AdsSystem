from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.advertising.models import Campaign, DailySpending


class Command(BaseCommand):
    help = 'Reset daily budgets for all campaigns (typically run via cron at midnight)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Date to reset budgets for (YYYY-MM-DD format). Defaults to today.',
        )
        parser.add_argument(
            '--campaign-id',
            type=str,
            help='Reset budget for specific campaign only',
        )

    def handle(self, *args, **options):
        date_str = options.get('date')
        campaign_id = options.get('campaign_id')
        
        if date_str:
            try:
                target_date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                self.stdout.write(
                    self.style.ERROR('Invalid date format. Use YYYY-MM-DD')
                )
                return
        else:
            target_date = timezone.now().date()

        # Get campaigns to reset
        campaigns = Campaign.objects.filter(status='active')
        if campaign_id:
            campaigns = campaigns.filter(id=campaign_id)

        reset_count = 0
        for campaign in campaigns:
            # Reset budget exceeded flag for the target date
            daily_spending, created = DailySpending.objects.get_or_create(
                campaign=campaign,
                date=target_date,
                defaults={'amount_spent': 0, 'budget_exceeded': False}
            )
            
            if not created and daily_spending.budget_exceeded:
                daily_spending.budget_exceeded = False
                daily_spending.save()
                reset_count += 1
                
                self.stdout.write(
                    f'Reset budget for campaign: {campaign.name} on {target_date}'
                )

        if reset_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully reset daily budgets for {reset_count} campaigns on {target_date}'
                )
            )
        else:
            self.stdout.write(
                f'No campaigns needed budget reset on {target_date}'
            ) 