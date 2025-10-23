from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html

from .models import Firm, FirmServiceHistory
from core.utils import generate_secure_password, log_activity
from core.models import ProvisionedCredential
from core.admin_filters import FirmStatusFilter


def generate_username_from_firm_name(firm_name):
    """Generate unique username from firm name"""
    User = get_user_model()
    base = firm_name.lower().replace(' ', '_')
    base = ''.join(ch for ch in base if ch.isalnum() or ch == '_') or 'firma'
    
    username = base
    suffix = 0
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base}{suffix}"
    
    return username


@admin.register(Firm)
class FirmAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'city', 'status_display', 'registration_date')
    list_filter = (FirmStatusFilter, 'city')
    search_fields = ('name', 'contact_person', 'email', 'tax_number')
    readonly_fields = ('registration_date', 'updated_at', 'unique_id', 'user')
    actions = ['set_active', 'set_inactive']
    
    fieldsets = (
        ('Firma Bilgileri', {
            'fields': ('name', 'tax_number', 'status'),
            'description': 'Firma adı zorunludur. Diğer alanlar isteğe bağlıdır.'
        }),
        ('İletişim Bilgileri', {
            'fields': ('contact_person', 'contact_person_title', 'phone', 'email', 'website'),
            'classes': ('collapse',),
        }),
        ('Adres Bilgileri', {
            'fields': ('address', 'city', 'country'),
            'classes': ('collapse',),
        }),
        ('Sistem Bilgileri', {
            'fields': ('user', 'registration_date', 'updated_at', 'unique_id'),
            'classes': ('collapse',),
            'description': 'Kullanıcı hesabı firma kaydedilirken otomatik oluşturulur.'
        }),
    )
    
    # Hide user field from add form, show in edit form
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing existing firm
            return self.readonly_fields
        else:  # Creating new firm
            return ('registration_date', 'updated_at', 'unique_id')
    
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if not obj:  # Creating new firm - hide user field
            return tuple(
                (name, {**opts, 'fields': tuple(f for f in opts['fields'] if f != 'user')})
                for name, opts in fieldsets
            )
        return fieldsets
    
    def status_display(self, obj):
        """Display status with visual indicators"""
        status_colors = {
            'active': ('#10b981', '✓ Aktif'),
            'inactive': ('#ef4444', '✗ Pasif'),
        }
        color, label = status_colors.get(obj.status, ('#6b7280', obj.get_status_display()))
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color, label
        )
    status_display.short_description = 'Durum'
    status_display.admin_order_field = 'status'

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        if is_new and not obj.user:
            # Auto-create user account for new firms
            User = get_user_model()
            username = generate_username_from_firm_name(obj.name)
            password = generate_secure_password(length=14)
            
            # Use email if provided, otherwise generate a placeholder
            email = obj.email if obj.email else f'{username}@placeholder.local'
            
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type='firma'
            )
            
            ProvisionedCredential.objects.create(
                user=user,
                username=username,
                password_plain=password,
                is_admin=False,
            )
            
            obj.user = user
            obj.save(update_fields=['user'])
            
            # Show success message with credentials
            if obj.email:
                self.message_user(request, 
                    f'✅ Firma oluşturuldu: {obj.name}\n'
                    f'Kullanıcı adı: {username}\n'
                    f'Şifre: {password}\n'
                    f'Bu bilgileri firmaya iletin.',
                    level='SUCCESS')
            else:
                self.message_user(request, 
                    f'⚠️ Firma oluşturuldu ancak e-posta adresi girilmedi.\n'
                    f'Kullanıcı adı: {username}\n'
                    f'Şifre: {password}\n'
                    f'Lütfen firma bilgilerini güncelleyerek geçerli bir e-posta adresi ekleyin.',
                    level='WARNING')
            
            log_activity(request.user, 'create', f'Firma için kullanıcı oluşturuldu: {obj.name} -> {username}')
    
    def delete_model(self, request, obj):
        """
        Override to ensure associated user is deleted when a firm is deleted.
        This is called when deleting a single firm via admin.
        """
        user = obj.user
        firm_name = obj.name
        super().delete_model(request, obj)
        if user:
            username = user.username
            user.delete()
            log_activity(request.user, 'delete', f'Firma ve kullanıcı silindi: {firm_name} -> {username}')
    
    def delete_queryset(self, request, queryset):
        """
        Override to ensure associated users are deleted when firms are bulk deleted.
        This is called when using 'delete selected' action on multiple firms.
        """
        # Collect user IDs before deletion
        users_to_delete = []
        for firm in queryset:
            if firm.user:
                users_to_delete.append(firm.user)
        
        # Delete firms (this will call the model's delete method for each)
        count = queryset.count()
        for firm in queryset:
            firm.delete()  # This will trigger the custom delete() method
        
        log_activity(request.user, 'delete', f'Toplu silme: {count} firma ve ilişkili kullanıcılar silindi')
    
    def set_active(self, request, queryset):
        """Set selected firms as active"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} firma aktif hale getirildi.')
        log_activity(request.user, 'update', f'Toplu aktifleştirme: {updated} firma')
    set_active.short_description = '✓ Seçili firmaları aktif yap'
    
    def set_inactive(self, request, queryset):
        """Set selected firms as inactive (passive)"""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'{updated} firma pasif hale getirildi.')
        log_activity(request.user, 'update', f'Toplu pasifleştirme: {updated} firma')
    set_inactive.short_description = '✗ Seçili firmaları pasif yap'
    
    def has_module_permission(self, request):
        """Allow staff users with permissions to access this module"""
        return request.user.is_superuser or (request.user.is_staff and (
            request.user.has_perm('firms.view_firm') or
            request.user.has_perm('firms.add_firm') or
            request.user.has_perm('firms.change_firm')
        ))
    
    def has_view_permission(self, request, obj=None):
        """Allow viewing for users with view or change permission"""
        return request.user.is_superuser or request.user.has_perm('firms.view_firm') or request.user.has_perm('firms.change_firm')
    
    def has_add_permission(self, request):
        """Allow adding for users with add permission"""
        return request.user.is_superuser or request.user.has_perm('firms.add_firm')
    
    def has_change_permission(self, request, obj=None):
        """Allow editing for users with change permission"""
        return request.user.is_superuser or request.user.has_perm('firms.change_firm')
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers"""
        return request.user.is_superuser

@admin.register(FirmServiceHistory)
class FirmServiceHistoryAdmin(admin.ModelAdmin):
    list_display = ('firm', 'service_type', 'service_date', 'completion_date', 'created_at')
    list_filter = ('service_type', 'completion_date')
    search_fields = ('firm__name', 'service_type', 'description')
    date_hierarchy = 'service_date'  # Date filter at top - removed from list_filter to avoid duplication
    
    def get_queryset(self, request):
        """Optimize with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('firm')