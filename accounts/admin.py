from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, UserProfile
from core.admin_filters import ActiveStatusFilter, StaffStatusFilter

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """User management - Add users (admins use AdminUserProxy section)"""
    list_display = ('username', 'email', 'user_type', 'active_status_display', 'date_joined')
    list_filter = ('user_type', ActiveStatusFilter, StaffStatusFilter, 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    
    # Custom action to view inactive accounts
    actions = ['activate_users', 'deactivate_users', 'activate_firms', 'deactivate_firms']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Ek Bilgiler', {
            'fields': ('user_type', 'phone', 'email_verified')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'user_type', 'first_name', 'last_name'),
        }),
    )
    
    def active_status_display(self, obj):
        """Display active status with visual indicators - shows firm status for firma users"""
        # For firma-type users, show firm status
        if obj.user_type == 'firma':
            try:
                firm_status = obj.firm.status
                status_display = {
                    'active': ('#10b981', '✓ Aktif'),
                    'inactive': ('#ef4444', '✗ Pasif'),
                }
                color, label = status_display.get(firm_status, ('#6b7280', 'Bilinmiyor'))
                return format_html(
                    '<span style="color: {}; font-weight: 600;">{}</span>',
                    color, label
                )
            except Exception:
                # If no firm exists, show user's is_active status
                return format_html(
                    '<span style="color: #ef4444; font-weight: 600;">✗ Firma Yok</span>'
                )
        
        # For admin users, show is_active status
        if obj.is_active:
            return format_html(
                '<span style="color: #10b981; font-weight: 600;">✓ Aktif</span>'
            )
        return format_html(
            '<span style="color: #ef4444; font-weight: 600;">✗ Pasif</span>'
        )
    active_status_display.short_description = 'Durum'
    active_status_display.admin_order_field = 'is_active'
    
    def get_queryset(self, request):
        """
        Show all users (active and inactive) in the listing.
        Use the 'is_active' filter in sidebar to filter by status.
        Optimized with select_related to avoid N+1 queries for firm status.
        """
        qs = super().get_queryset(request)
        # Use select_related to efficiently load firm data for firma users
        qs = qs.select_related('firm')
        return qs
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} kullanıcı aktif hale getirildi.')
    activate_users.short_description = '✅ Seçili kullanıcıları aktif et'
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users (soft delete)"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} kullanıcı pasif hale getirildi.')
    deactivate_users.short_description = '🚫 Seçili kullanıcıları pasif et'
    
    def activate_firms(self, request, queryset):
        """Activate selected firms (for firma-type users)"""
        updated = 0
        for user in queryset.filter(user_type='firma'):
            try:
                if hasattr(user, 'firm'):
                    user.firm.status = 'active'
                    user.firm.save(update_fields=['status'])
                    updated += 1
            except Exception:
                pass
        if updated > 0:
            self.message_user(request, f'{updated} firma aktif hale getirildi.')
        else:
            self.message_user(request, 'Seçili kullanıcılar arasında firma bulunamadı.', level='WARNING')
    activate_firms.short_description = '✅ Seçili firmaları aktif et'
    
    def deactivate_firms(self, request, queryset):
        """Deactivate selected firms (for firma-type users)"""
        updated = 0
        for user in queryset.filter(user_type='firma'):
            try:
                if hasattr(user, 'firm'):
                    user.firm.status = 'inactive'
                    user.firm.save(update_fields=['status'])
                    updated += 1
            except Exception:
                pass
        if updated > 0:
            self.message_user(request, f'{updated} firma pasif hale getirildi.')
        else:
            self.message_user(request, 'Seçili kullanıcılar arasında firma bulunamadı.', level='WARNING')
    deactivate_firms.short_description = '🚫 Seçili firmaları pasif et'
    
    def has_module_permission(self, request):
        return request.user.is_superuser
    
    def has_add_permission(self, request):
        return request.user.is_superuser  # Allow superusers to add users
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

class UserProfileActiveFilter(admin.SimpleListFilter):
    """Custom filter for user active status in UserProfile"""
    title = 'Kullanıcı Durumu'
    parameter_name = 'user_active'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Aktif'),
            ('0', 'Pasif'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(user__is_active=True)
        if self.value() == '0':
            return queryset.filter(user__is_active=False)
        return queryset


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_user_type', 'get_user_status', 'has_avatar')
    list_filter = ('user__user_type', UserProfileActiveFilter)
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name', 'bio')
    readonly_fields = ('user',)
    
    def get_queryset(self, request):
        """Optimize with select_related to avoid N+1 queries"""
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    def get_user_type(self, obj):
        return obj.user.get_user_type_display()
    get_user_type.short_description = 'Kullanıcı Tipi'
    
    def get_user_status(self, obj):
        """Display user active status with visual indicator"""
        if obj.user.is_active:
            return format_html('<span style="color: #10b981; font-weight: 600;">✓ Aktif</span>')
        return format_html('<span style="color: #ef4444; font-weight: 600;">✗ Pasif</span>')
    get_user_status.short_description = 'Durum'
    get_user_status.admin_order_field = 'user__is_active'
    
    def has_avatar(self, obj):
        """Check if profile has avatar"""
        if obj.avatar:
            return format_html('<span style="color: #10b981;">✓</span>')
        return format_html('<span style="color: #6b7280;">-</span>')
    has_avatar.short_description = 'Avatar'
    has_avatar.admin_order_field = 'avatar'
    
    def has_module_permission(self, request):
        return request.user.is_superuser