# Admin Management - Yönetici Yönetimi
# Sadece superuser'lar yönetici ekleyebilir ve yöneticileri görebilir

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.urls import reverse
from core.utils import generate_secure_password, log_activity
from core.models import ProvisionedCredential
from .models import CustomUser

User = get_user_model()


class AdminUserProxy(CustomUser):
    """Proxy model for admin users only"""
    class Meta:
        proxy = True
        verbose_name = 'Yönetici'
        verbose_name_plural = 'Yöneticiler'


@admin.register(AdminUserProxy)
class AdminUserManagementAdmin(admin.ModelAdmin):
    """
    Özel Yönetici Yönetimi Admin
    - Sadece admin tipi kullanıcıları gösterir
    - Sadece superuser'lar erişebilir
    - Otomatik username ve password oluşturur
    """
    
    list_display = ('username_display', 'email', 'full_name_display', 'is_active', 'date_joined', 'credentials_link')
    list_filter = ('is_active', 'date_joined', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('username', 'date_joined', 'last_login', 'credential_info')
    actions = ['activate_admins', 'deactivate_admins', 'delete_selected']
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Yetkiler', {
            'fields': ('is_active', 'is_superuser', 'is_staff')
        }),
        ('Kimlik Bilgileri', {
            'fields': ('credential_info',),
            'classes': ('collapse',)
        }),
        ('Tarihler', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Yeni Yönetici Oluştur', {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'is_superuser'),
            'description': 'Kullanıcı adı ve şifre otomatik oluşturulacaktır.'
        }),
    )
    
    def get_queryset(self, request):
        """Sadece admin tipi kullanıcıları göster"""
        qs = super().get_queryset(request)
        return qs.filter(user_type='admin', is_staff=True)
    
    def has_module_permission(self, request):
        """Sadece superuser'lar bu modülü görebilir"""
        return request.user.is_superuser
    
    def has_view_permission(self, request, obj=None):
        """Sadece superuser'lar görebilir"""
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        """Sadece superuser'lar ekleyebilir"""
        return request.user.is_superuser
    
    def has_change_permission(self, request, obj=None):
        """Sadece superuser'lar değiştirebilir"""
        return request.user.is_superuser
    
    def has_delete_permission(self, request, obj=None):
        """Sadece superuser'lar silebilir"""
        return request.user.is_superuser
    
    def get_fieldsets(self, request, obj=None):
        """Yeni ekleme için özel fieldsets"""
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
    
    def username_display(self, obj):
        """Username with badge"""
        if obj.is_superuser:
            return format_html(
                '<strong>{}</strong> <span style="background: #10b981; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600;">SÜPER ADMİN</span>',
                obj.username
            )
        return format_html('<strong>{}</strong>', obj.username)
    username_display.short_description = 'Kullanıcı Adı'
    
    def full_name_display(self, obj):
        """Full name or dash"""
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}".strip()
        return '-'
    full_name_display.short_description = 'Ad Soyad'
    
    def credentials_link(self, obj):
        """Link to credentials"""
        try:
            credential = ProvisionedCredential.objects.get(user=obj)
            url = reverse('admin:core_provisionedcredential_change', args=[credential.pk])
            return format_html(
                '<a href="{}" style="background: #3b82f6; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-decoration: none; font-weight: 600;">🔑 Kimlik Bilgileri</a>',
                url
            )
        except ProvisionedCredential.DoesNotExist:
            return format_html('<span style="color: #6c757d;">Bilgi yok</span>')
    credentials_link.short_description = 'Kimlik Bilgileri'
    
    def credential_info(self, obj):
        """Display credentials in readonly field"""
        try:
            credential = ProvisionedCredential.objects.get(user=obj)
            return format_html(
                '''
                <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #3b82f6;">
                    <p style="margin: 0 0 0.75rem 0;"><strong style="color: #1e3a8a;">👤 Kullanıcı Adı:</strong> <code style="background: #e9ecef; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 1rem;">{}</code></p>
                    <p style="margin: 0;"><strong style="color: #1e3a8a;">🔑 Şifre:</strong> <code style="background: #e9ecef; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 1rem;">{}</code></p>
                    <p style="margin: 0.75rem 0 0 0; color: #6c757d; font-size: 0.875rem;">
                        <i class="fas fa-info-circle"></i> Bu bilgileri yöneticiye güvenli bir şekilde iletin.
                    </p>
                </div>
                ''',
                credential.username,
                credential.password_plain or 'Şifre değiştirilmiş'
            )
        except ProvisionedCredential.DoesNotExist:
            return format_html('<p style="color: #6c757d;">Kimlik bilgisi bulunamadı.</p>')
    credential_info.short_description = 'Giriş Bilgileri'
    
    def save_model(self, request, obj, form, change):
        """Otomatik username ve password oluştur"""
        is_new = obj.pk is None
        
        if is_new:
            # Auto-generate username (admin1, admin2, etc.)
            base = 'admin'
            suffix = 1
            username = f"{base}{suffix}"
            
            while User.objects.filter(username=username).exists():
                suffix += 1
                username = f"{base}{suffix}"
            
            obj.username = username
            
            # Auto-generate password
            password = generate_secure_password(length=14)
            obj.set_password(password)
            
            # Set as admin and staff
            obj.user_type = 'admin'
            obj.is_staff = True
            
            # Save first
            super().save_model(request, obj, form, change)
            
            # Store credentials
            ProvisionedCredential.objects.create(
                user=obj,
                username=obj.username,
                password_plain=password,
                is_admin=True,
            )
            
            # Log activity
            log_activity(request.user, 'create', f'Yeni yönetici oluşturuldu: {obj.username}')
            
            # Success message
            self.message_user(
                request,
                format_html(
                    '✅ Yönetici başarıyla oluşturuldu! Kullanıcı adı: <strong>{}</strong> | Şifre: <strong>{}</strong>',
                    obj.username,
                    password
                )
            )
        else:
            super().save_model(request, obj, form, change)
            log_activity(request.user, 'update', f'Yönetici güncellendi: {obj.username}')
    
    def activate_admins(self, request, queryset):
        """Toplu aktifleştirme"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} yönetici aktifleştirildi.')
    activate_admins.short_description = '✅ Seçili yöneticileri aktifleştir'
    
    def deactivate_admins(self, request, queryset):
        """Toplu pasifleştirme"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} yönetici pasifleştirildi.')
    deactivate_admins.short_description = '❌ Seçili yöneticileri pasifleştir'

