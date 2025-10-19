from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.utils import generate_secure_password

class Command(BaseCommand):
    help = 'İlk yönetici hesabını oluşturur'
    
    def handle(self, *args, **options):
        User = get_user_model()
        
        if not User.objects.filter(user_type='admin').exists():
            password = generate_secure_password()
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@byfmuhendislik.com',
                password=password,
                user_type='admin'
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Admin kullanıcısı oluşturuldu!\nKullanıcı adı: admin\nŞifre: {password}'
                )
            )
        else:
            self.stdout.write(self.style.WARNING('Admin kullanıcısı zaten mevcut.'))