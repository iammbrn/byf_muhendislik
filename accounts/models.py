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
    
    def __str__(self):
        return f"{self.user.username} Profili"