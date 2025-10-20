from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Yönetici'),
        ('firma', 'Firma'),
    )
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='firma')
    phone = models.CharField(max_length=15, blank=True, verbose_name='Telefon')
    email_verified = models.BooleanField(default=False, verbose_name='E-posta Doğrulandı')
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        indexes = [
            models.Index(fields=['user_type', 'is_active'], name='user_type_active_idx'),
            models.Index(fields=['-date_joined'], name='user_date_joined_idx'),
            models.Index(fields=['email'], name='user_email_lookup_idx'),
        ]
        db_table_comment = 'Kullanıcılar - sistem erişim hesapları'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Profil Resmi')
    bio = models.TextField(blank=True, verbose_name='Hakkımda')
    address = models.TextField(blank=True, verbose_name='Adres')
    
    class Meta:
        verbose_name = 'Kullanıcı Profili'
        verbose_name_plural = 'Kullanıcı Profilleri'
        db_table_comment = 'Kullanıcı profil bilgileri - ek detaylar'
    
    def __str__(self):
        return f"{self.user.username} Profili"