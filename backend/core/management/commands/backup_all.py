from django.core.management.base import BaseCommand
from django.conf import settings
import os
import datetime
import shutil


class Command(BaseCommand):
    help = 'Veritabanı ve media klasörü için basit yedekleme oluşturur.'

    def handle(self, *args, **options):
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = os.path.join(settings.BASE_DIR, 'database', 'backup')
        os.makedirs(backup_dir, exist_ok=True)

        # Media backup (zip)
        media_src = settings.MEDIA_ROOT
        media_zip = os.path.join(backup_dir, f'media_{timestamp}')
        if os.path.isdir(media_src):
            shutil.make_archive(media_zip, 'zip', media_src)
            self.stdout.write(self.style.SUCCESS(f'Media backup: {media_zip}.zip'))
        else:
            self.stdout.write(self.style.WARNING('Media klasörü bulunamadı.'))

        # DB backup hint (psql/pg_dump expected in deployment scripts)
        self.stdout.write(self.style.WARNING('DB backup için deployment/scripts/backup.sh kullanılmalı.'))

