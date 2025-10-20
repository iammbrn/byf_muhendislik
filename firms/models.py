from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator
import uuid

class Firm(models.Model):
    STATUS_CHOICES = (
        ('active', 'Aktif'),
        ('inactive', 'Pasif'),
    )
    
    name = models.CharField(max_length=255, verbose_name='Firma Adı', db_index=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='firm',
        null=True,  # Allow null for initial creation
        blank=True,  # Allow blank in forms
        help_text='Kullanıcı hesabı otomatik olarak oluşturulur'
    )
    tax_number = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name='Vergi No',
        validators=[RegexValidator(regex=r'^\d{10}$', message='Vergi numarası 10 haneli olmalıdır.', code='invalid_tax_number')],
        help_text='10 haneli vergi numarası (opsiyonel)'
    )
    phone = models.CharField(
        max_length=15, 
        blank=True,  # Make optional
        verbose_name='Telefon',
        validators=[RegexValidator(regex=r'^\+?[\d\s\-()]{10,15}$', message='Geçerli bir telefon numarası girin.')]
    )
    email = models.EmailField(blank=True, verbose_name='E-posta', validators=[EmailValidator()])  # Make optional
    address = models.TextField(blank=True, verbose_name='Adres')  # Make optional
    city = models.CharField(max_length=100, blank=True, verbose_name='Şehir')  # Make optional
    country = models.CharField(max_length=100, default='Türkiye', blank=True, verbose_name='Ülke')
    website = models.URLField(blank=True, verbose_name='Web Sitesi')
    contact_person = models.CharField(max_length=255, blank=True, verbose_name='Yetkili Kişi')  # Make optional
    contact_person_title = models.CharField(max_length=255, blank=True, verbose_name='Yetkili Unvanı')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    registration_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    class Meta:
        verbose_name = 'Firma'
        verbose_name_plural = 'Firmalar'
        ordering = ['-registration_date']
        indexes = [
            models.Index(fields=['-registration_date'], name='firm_reg_date_idx'),
            models.Index(fields=['status', '-registration_date'], name='firm_status_date_idx'),
            models.Index(fields=['city', 'status'], name='firm_city_status_idx'),
        ]
        db_table_comment = 'Firma bilgileri - müşteri firmaların kayıtları'
    
    def __str__(self):
        return self.name
    
    @property
    def is_active(self):
        return self.status == 'active'
    
    def delete(self, *args, **kwargs):
        """
        Override delete to also remove associated user.
        When a firm is deleted, the associated user should also be deleted
        to maintain data consistency.
        """
        user = self.user
        # Delete the firm first
        result = super().delete(*args, **kwargs)
        # Then delete the associated user if it exists
        if user:
            user.delete()
        return result
    
    def clean(self):
        """Validate firm data"""
        super().clean()
        
        # Ensure user is firma type (if user is assigned)
        if self.user and self.user.user_type != 'firma':
            raise ValidationError({
                'user': 'Firma için sadece firma tipi kullanıcılar atanabilir.'
            })
        
        # Validate tax number format if provided
        if self.tax_number and not self.tax_number.isdigit():
            raise ValidationError({
                'tax_number': 'Vergi numarası sadece rakam içermelidir.'
            })

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
        indexes = [
            models.Index(fields=['firm', '-service_date'], name='firmhist_firm_date_idx'),
        ]
        db_table_comment = 'Firma hizmet geçmişi - eski kayıtlar için'
    
    def __str__(self):
        return f"{self.firm.name} - {self.service_type}"