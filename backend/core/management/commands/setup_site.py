from django.core.management.base import BaseCommand
from core.models import SiteSettings


class Command(BaseCommand):
    help = 'Site ayarlarını başlangıç değerleriyle oluşturur'

    def handle(self, *args, **options):
        if SiteSettings.objects.exists():
            self.stdout.write(self.style.WARNING('Site ayarları zaten mevcut.'))
            return

        site = SiteSettings.objects.create(
            site_name='BYF Mühendislik',
            site_description='Elektriksel Periyodik Kontrol, Trafo Müşavirlik ve Elektrik Proje Çizimi alanlarında profesyonel hizmet.',
            contact_email='info@byfmuhendislik.com',
            contact_phone='+905551234567',
            address='Gazi Mustafa Kemal, Bakırçay Üniversitesi, 35660 Menemen/İzmir',
            whatsapp_number='905551234567',
            linkedin_url='https://linkedin.com/company/byf-muhendislik',
            instagram_url='https://instagram.com/byf_muhendislik',
        )
        self.stdout.write(self.style.SUCCESS(f'Site ayarları oluşturuldu: {site.site_name}'))

