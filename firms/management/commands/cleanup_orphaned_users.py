"""
Management command to clean up orphaned users (users without firms).
This fixes the issue where firms were deleted but their users remained.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from firms.models import Firm

User = get_user_model()


class Command(BaseCommand):
    help = 'Clean up orphaned users (firma-type users without associated firms)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find users without firms
        existing_firm_user_ids = Firm.objects.values_list('user_id', flat=True).filter(user__isnull=False)
        orphaned_users = User.objects.filter(user_type='firma').exclude(id__in=existing_firm_user_ids)
        
        count = orphaned_users.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No orphaned users found'))
            return
        
        self.stdout.write(self.style.WARNING(f'\nFound {count} orphaned user(s):'))
        for user in orphaned_users:
            self.stdout.write(f'  - {user.username} (email: {user.email}, joined: {user.date_joined})')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] No users were deleted'))
            self.stdout.write(self.style.NOTICE('Run without --dry-run to actually delete these users'))
        else:
            # Delete orphaned users
            deleted_usernames = [u.username for u in orphaned_users]
            orphaned_users.delete()
            
            self.stdout.write(self.style.SUCCESS(f'\nDeleted {count} orphaned user(s):'))
            for username in deleted_usernames:
                self.stdout.write(f'  - {username}')
            
            self.stdout.write(self.style.SUCCESS('\nCleanup complete!'))

