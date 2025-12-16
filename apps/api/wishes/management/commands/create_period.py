"""
Management command to create periods and assign wishes.
This should be run automatically (e.g., via cron) at the start of each period.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
import random

from wishes.models import Category, Wish, Match, Period, Assignment
from users.models import User


class Command(BaseCommand):
    help = 'Create new periods and assign wishes randomly'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days for the period (default: 30)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview assignments without saving'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        today = timezone.now().date()
        period_start = today
        period_end = period_start + timedelta(days=days)
        
        self.stdout.write(self.style.SUCCESS(
            f'\n=== Creating Period: {period_start} to {period_end} ==='
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved'))
        
        # Create global period for public matches
        if not dry_run:
            global_period = Period.objects.create(
                match=None,
                start_date=period_start,
                end_date=period_end,
                is_active=True
            )
            self.stdout.write(self.style.SUCCESS(f'Created global period: {global_period}'))
        else:
            global_period = None
            self.stdout.write('Would create global period')
        
        # Process private matches
        private_matches = Match.objects.filter(
            mode=Match.MODE_PRIVATE,
            status=Match.STATUS_ACCEPTED
        ).select_related('user1', 'user2')
        
        self.stdout.write(f'\nProcessing {private_matches.count()} private matches...')
        
        for match in private_matches:
            # Create period for this match
            match_days = match.private_period_days or days
            match_period_end = period_start + timedelta(days=match_days)
            
            if not dry_run:
                match_period = Period.objects.create(
                    match=match,
                    start_date=period_start,
                    end_date=match_period_end,
                    is_active=True
                )
            else:
                match_period = None
            
            # Assign wishes for user1
            assignments_created = self._assign_wishes_for_match(
                match, match.user1, match.user2, match_period, match_period_end, dry_run
            )
            
            # Assign wishes for user2
            assignments_created += self._assign_wishes_for_match(
                match, match.user2, match.user1, match_period, match_period_end, dry_run
            )
            
            self.stdout.write(f'  {match}: {assignments_created} assignments')
        
        # Process public matches
        public_users = User.objects.filter(
            is_active=True,
            is_public_mode_active=True
        )
        
        self.stdout.write(f'\nProcessing {public_users.count()} users in public mode...')
        
        for user in public_users:
            # Find accepted public matches for this user
            public_matches = Match.objects.filter(
                Q(user1=user) | Q(user2=user),
                mode=Match.MODE_PUBLIC,
                status=Match.STATUS_ACCEPTED
            )
            
            assignments_created = 0
            for match in public_matches:
                # Determine the other user in the match
                other_user = match.user2 if match.user1 == user else match.user1
                
                # Assign wishes
                assignments_created += self._assign_wishes_for_match(
                    None, user, other_user, global_period, period_end, dry_run
                )
            
            if assignments_created > 0:
                self.stdout.write(f'  {user.nickname}: {assignments_created} assignments')
        
        self.stdout.write(self.style.SUCCESS('\n=== Period creation complete ===\n'))

    def _assign_wishes_for_match(self, match, wish_owner, executor, period, due_date, dry_run):
        """
        Assign wishes from wish_owner to executor.
        Returns number of assignments created.
        """
        assignments_created = 0
        
        # Get categories (either from match or all active categories)
        if match and match.mode == Match.MODE_PRIVATE:
            categories = match.private_categories.all()
        else:
            categories = Category.objects.filter(is_active=True)
            # Filter adult categories for minors
            if not executor.is_adult:
                categories = categories.filter(is_adult=False)
        
        for category in categories:
            # Get active wishes from this category
            wishes = Wish.objects.filter(
                user=wish_owner,
                category=category,
                is_active=True
            )
            
            # Filter adult wishes for minor executors
            if not executor.is_adult:
                wishes = wishes.filter(category__is_adult=False)
            
            # Randomly select up to max_wishes_per_period
            wish_list = list(wishes)
            if wish_list:
                max_wishes = category.max_wishes_per_period
                selected_wishes = random.sample(
                    wish_list,
                    min(len(wish_list), max_wishes)
                )
                
                for wish in selected_wishes:
                    if not dry_run:
                        Assignment.objects.create(
                            period=period,
                            wish=wish,
                            assigned_to=executor,
                            due_date=due_date,
                            is_completed=False,
                            is_rejected=False
                        )
                    assignments_created += 1
        
        return assignments_created
