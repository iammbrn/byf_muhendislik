from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid

class Service(models.Model):
    SERVICE_TYPES = (
        ('electrical_control', 'Elektriksel Periyodik Kontrol'),
        ('transformer_consultancy', 'Trafo Müşavirlik'),
        ('electrical_design', 'Elektrik Proje Çizimi'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('cancelled', 'İptal Edildi'),
    )
    
    name = models.CharField(max_length=255, verbose_name='Hizmet Adı')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES, verbose_name='Hizmet Türü')
    description = models.TextField(verbose_name='Açıklama')
    firm = models.ForeignKey('firms.Firm', on_delete=models.CASCADE, related_name='services')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True, verbose_name='Talep Tarihi')
    start_date = models.DateField(null=True, blank=True, verbose_name='Başlangıç Tarihi')
    completion_date = models.DateField(null=True, blank=True, verbose_name='Tamamlanma Tarihi')
    assigned_admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name='assigned_services')
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    notes = models.TextField(blank=True, verbose_name='Notlar')
    
    class Meta:
        verbose_name = 'Hizmet'
        verbose_name_plural = 'Hizmetler'
        ordering = ['-request_date']
        indexes = [
            models.Index(fields=['-request_date'], name='service_request_date_idx'),
            models.Index(fields=['firm', 'status'], name='service_firm_status_idx'),
            models.Index(fields=['status', '-request_date'], name='service_status_date_idx'),
            models.Index(fields=['-completion_date'], name='service_completion_idx'),
        ]
        db_table_comment = 'Hizmet kayıtları - müşteri hizmetlerinin detayları'
    
    def __str__(self):
        return f"{self.firm.name} - {self.get_service_type_display()}"
    
    def clean(self):
        """Validate service data"""
        super().clean()
        
        # Completion date must be after start date
        if self.start_date and self.completion_date:
            if self.completion_date < self.start_date:
                raise ValidationError({
                    'completion_date': 'Tamamlanma tarihi başlangıç tarihinden önce olamaz.'
                })
        
        # Assigned admin must be admin type
        if self.assigned_admin and self.assigned_admin.user_type != 'admin':
            raise ValidationError({
                'assigned_admin': 'Sadece admin tipi kullanıcılar atanabilir.'
            })

class ServiceRequest(models.Model):
    PRIORITY_CHOICES = (
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('urgent', 'Acil'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Bekliyor'),
        ('approved', 'Onaylandı'),
        ('rejected', 'Reddedildi'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
    )
    
    firm = models.ForeignKey('firms.Firm', on_delete=models.CASCADE, related_name='service_requests')
    service_type = models.CharField(max_length=50, choices=Service.SERVICE_TYPES, verbose_name='Hizmet Türü')
    title = models.CharField(max_length=255, verbose_name='Talep Başlığı')
    description = models.TextField(verbose_name='Talep Açıklaması')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Durum')
    request_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tracking_code = models.CharField(max_length=20, unique=True, blank=True)
    requested_completion_date = models.DateField(null=True, blank=True, verbose_name='İstenen Tamamlanma Tarihi')
    admin_response = models.TextField(blank=True, verbose_name='Yönetici Yanıtı')
    responded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                      null=True, blank=True, related_name='responded_requests')
    
    class Meta:
        verbose_name = 'Hizmet Talebi'
        verbose_name_plural = 'Hizmet Talepleri'
        ordering = ['-request_date']
        indexes = [
            models.Index(fields=['-request_date'], name='svcreq_request_date_idx'),
            models.Index(fields=['firm', 'status'], name='svcreq_firm_status_idx'),
            models.Index(fields=['status', '-request_date'], name='svcreq_status_date_idx'),
            models.Index(fields=['tracking_code'], name='svcreq_tracking_code_idx'),
        ]
        db_table_comment = 'Hizmet talepleri - müşterilerden gelen yeni hizmet istekleri'
    
    def __str__(self):
        return f"{self.firm.name} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            # Simple deterministic tracking code: SR-<first8uuid>
            self.tracking_code = f"SR-{str(self.unique_id)[:8].upper()}"
        super().save(*args, **kwargs)