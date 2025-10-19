from django.db import models
from django.conf import settings
import uuid

class Firm(models.Model):
    STATUS_CHOICES = (
        ('active', 'Aktif'),
        ('inactive', 'Pasif'),
        ('suspended', 'Askıda'),
    )
    
    name = models.CharField(max_length=255, verbose_name='Firma Adı')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='firm')
    tax_number = models.CharField(max_length=20, blank=True, verbose_name='Vergi No')
    phone = models.CharField(max_length=15, verbose_name='Telefon')
    email = models.EmailField(verbose_name='E-posta')
    address = models.TextField(verbose_name='Adres')
    city = models.CharField(max_length=100, verbose_name='Şehir')
    country = models.CharField(max_length=100, default='Türkiye', verbose_name='Ülke')
    website = models.URLField(blank=True, verbose_name='Web Sitesi')
    contact_person = models.CharField(max_length=255, verbose_name='Yetkili Kişi')
    contact_person_title = models.CharField(max_length=255, blank=True, verbose_name='Yetkili Unvanı')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    class Meta:
        verbose_name = 'Firma'
        verbose_name_plural = 'Firmalar'
        ordering = ['-registration_date']
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        return self.status == 'active'

class FirmServiceHistory(models.Model):
    firm = models.ForeignKey(Firm, on_delete=models.CASCADE, related_name='service_history')
    service_type = models.CharField(max_length=255, verbose_name='Hizmet Türü')
    description = models.TextField(verbose_name='Açıklama')
    service_date = models.DateField(verbose_name='Hizmet Tarihi')
    completion_date = models.DateField(verbose_name='Tamamlanma Tarihi')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Firma Hizmet Geçmişi'
        verbose_name_plural = 'Firma Hizmet Geçmişleri'
        ordering = ['-service_date']
    
    def __str__(self):
        return f"{self.firm.name} - {self.service_type}"