from django.db import models
from django.conf import settings

class SiteSettings(models.Model):
    site_name = models.CharField(max_length=255, default='BYF Mühendislik', verbose_name='Site Adı')
    site_description = models.TextField(blank=True, verbose_name='Site Açıklaması')
    contact_email = models.EmailField(verbose_name='İletişim E-postası')
    contact_phone = models.CharField(max_length=15, verbose_name='İletişim Telefonu')
    address = models.TextField(verbose_name='Adres')
    logo = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name='Logo')
    favicon = models.ImageField(upload_to='site/', blank=True, null=True, verbose_name='Favicon')
    hero_image = models.ImageField(
        upload_to='site/', 
        blank=True, 
        null=True, 
        verbose_name='Ana Sayfa Hero Görseli',
        help_text='Önerilen boyut: 1920x1080px veya 16:9 oran'
    )
    about_image = models.ImageField(
        upload_to='site/', 
        blank=True, 
        null=True, 
        verbose_name='Hakkımızda Sayfası Görseli',
        help_text='Önerilen boyut: 800x600px veya 4:3 oran'
    )
    facebook_url = models.URLField(blank=True, verbose_name='Facebook')
    twitter_url = models.URLField(blank=True, verbose_name='Twitter')
    linkedin_url = models.URLField(blank=True, verbose_name='LinkedIn')
    instagram_url = models.URLField(blank=True, verbose_name='Instagram')
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name='WhatsApp Numarası')
    google_analytics_id = models.CharField(max_length=32, blank=True, verbose_name='Google Analytics ID')
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Site Ayarı'
        verbose_name_plural = 'Site Ayarları'
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        if not self.pk and SiteSettings.objects.exists():
            return
        super().save(*args, **kwargs)


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=16, choices=ACTION_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Aktivite Kaydı'
        verbose_name_plural = 'Aktivite Kayıtları'

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"


class ProvisionedCredential(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provisioned_credentials')
    username = models.CharField(max_length=150)
    password_plain = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Oluşturulan Kimlik Bilgisi'
        verbose_name_plural = 'Oluşturulan Kimlik Bilgileri'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({'Admin' if self.is_admin else 'Firma'})"


class ContactMessage(models.Model):
    STATUS_CHOICES = (
        ('new', 'Yeni'),
        ('read', 'Okundu'),
        ('replied', 'Yanıtlandı'),
        ('archived', 'Arşivlendi'),
    )
    
    name = models.CharField(max_length=100, verbose_name='Ad')
    surname = models.CharField(max_length=100, verbose_name='Soyad')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    email = models.EmailField(verbose_name='E-posta')
    subject = models.CharField(max_length=200, verbose_name='Konu')
    message = models.TextField(verbose_name='Mesaj')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Durum')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Gönderim Tarihi')
    responded_at = models.DateTimeField(null=True, blank=True, verbose_name='Yanıtlanma Tarihi')
    response_note = models.TextField(blank=True, verbose_name='Yanıt Notu')
    
    class Meta:
        verbose_name = 'İletişim Mesajı'
        verbose_name_plural = 'İletişim Mesajları'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} {self.surname} - {self.subject}"
    
    @property
    def full_name(self):
        return f"{self.name} {self.surname}"


class ServiceCategory(models.Model):
    """Dinamik hizmet kategorileri - Hizmetlerimiz sayfası için"""
    
    ICON_CHOICES = (
        ('fa-bolt', 'Yıldırım'),
        ('fa-plug', 'Fiş'),
        ('fa-drafting-compass', 'Pergel'),
        ('fa-transformer', 'Transformatör'),
        ('fa-cogs', 'Dişliler'),
        ('fa-tools', 'Aletler'),
        ('fa-hard-hat', 'Baret'),
        ('fa-lightbulb', 'Ampul'),
        ('fa-solar-panel', 'Solar Panel'),
        ('fa-charging-station', 'Şarj İstasyonu'),
    )
    
    title = models.CharField(max_length=200, verbose_name='Hizmet Başlığı')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL Slug')
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, default='fa-cogs', verbose_name='İkon')
    subtitle = models.CharField(max_length=300, verbose_name='Alt Başlık')
    description = models.TextField(verbose_name='Açıklama')
    
    # Hizmet Kapsamı
    scope_items = models.TextField(
        verbose_name='Kapsam Maddeleri',
        help_text='Her satıra bir madde yazın'
    )
    
    # Avantajlar / Özellikler
    features = models.TextField(
        verbose_name='Avantajlar/Özellikler',
        help_text='Her satıra bir özellik yazın'
    )
    
    # Süreç Adımları (JSON formatında)
    process_steps = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Süreç Adımları',
        help_text='[{"title": "Adım 1", "description": "Açıklama"}] formatında'
    )
    
    # Standartlar
    standards = models.TextField(
        blank=True,
        verbose_name='Standartlar',
        help_text='Her satıra bir standart yazın'
    )
    
    order = models.IntegerField(default=0, verbose_name='Sıralama')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Hizmet Kategorisi'
        verbose_name_plural = 'Hizmet Kategorileri'
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def _text_field_to_list(self, field_value):
        """Helper: Convert newline-separated text to list"""
        if not field_value:
            return []
        return [item.strip() for item in field_value.split('\n') if item.strip()]
    
    def get_scope_list(self):
        """Kapsam maddelerini liste olarak döndür"""
        return self._text_field_to_list(self.scope_items)
    
    def get_features_list(self):
        """Avantajları liste olarak döndür"""
        return self._text_field_to_list(self.features)
    
    def get_standards_list(self):
        """Standartları liste olarak döndür"""
        return self._text_field_to_list(self.standards)
    
    def get_process_steps_safe(self):
        """Süreç adımlarını güvenli şekilde döndür"""
        if not self.process_steps:
            return []
        
        # JSON formatını kontrol et
        if isinstance(self.process_steps, list):
            # Her adımın title ve description içerdiğinden emin ol
            safe_steps = []
            for step in self.process_steps:
                if isinstance(step, dict):
                    safe_steps.append({
                        'title': str(step.get('title', 'Adım')),
                        'description': str(step.get('description', ''))
                    })
            return safe_steps
        
        return []


def team_member_image_path(instance, filename):
    """Ekip üyesi fotoğrafları için upload path"""
    import os
    ext = os.path.splitext(filename)[1]
    return f'team/{instance.slug}{ext}'


class TeamMember(models.Model):
    """Ekip üyeleri - Hakkımızda sayfası için"""
    
    name = models.CharField(max_length=200, verbose_name='Ad Soyad')
    slug = models.SlugField(max_length=200, unique=True, verbose_name='URL Slug')
    title = models.CharField(max_length=200, verbose_name='Ünvan/Pozisyon')
    bio = models.TextField(verbose_name='Biyografi/Açıklama')
    image = models.ImageField(
        upload_to=team_member_image_path,
        verbose_name='Fotoğraf',
        help_text='Tercihen kare (1:1) oran ve minimum 400x400px boyutunda'
    )
    email = models.EmailField(blank=True, verbose_name='E-posta')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    linkedin_url = models.URLField(blank=True, verbose_name='LinkedIn URL')
    
    order = models.IntegerField(default=0, verbose_name='Sıralama')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ekip Üyesi'
        verbose_name_plural = 'Ekip Üyeleri'
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.title}"