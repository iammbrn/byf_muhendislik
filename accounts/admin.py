from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser
from core.admin_filters import ActiveStatusFilter, StaffStatusFilter

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """User management - Add users (admins use AdminUserProxy section)"""
    list_display = ('username', 'email', 'user_type', 'active_status_display', 'date_joined')
    list_filter = ('user_type', ActiveStatusFilter, StaffStatusFilter, 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')
    change_form_template = 'admin/accounts/customuser/change_form.html'
    
    # CRITICAL: Override filter_horizontal to use normal SelectMultiple instead of FilteredSelectMultiple
    # This is required for our custom permissions UI to work properly
    filter_horizontal = ()
    
    # Custom action to view inactive accounts
    actions = ['activate_users', 'deactivate_users', 'activate_firms', 'deactivate_firms']
    
    # Override fieldsets to remove groups
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Kişisel Bilgiler', {'fields': ('first_name', 'last_name', 'email')}),
        ('İzinler', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('Önemli Tarihler', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',),
        }),
        ('Ek Bilgiler', {
            'fields': ('user_type', 'phone', 'email_verified'),
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
    
    def save_related(self, request, form, formsets, change):
        """
        CRITICAL: Override save_related to ensure user permissions are saved.
        Django saves ManyToMany fields (like user_permissions) in save_related, NOT save_model.
        This is because M2M relationships require the object to be saved first (to have an ID).
        """
        import logging
        logger = logging.getLogger(__name__)
        
        obj = form.instance
        
        # DEBUG: Log what we received from the form
        logger.info(f'📝 save_related called for user: {obj.username}')
        logger.info(f'📋 Form cleaned_data keys: {list(form.cleaned_data.keys())}')
        
        # Check if user_permissions is in the form data
        if 'user_permissions' in form.cleaned_data:
            selected_permissions = form.cleaned_data['user_permissions']
            logger.info(f'✅ user_permissions in cleaned_data: {selected_permissions.count()} permissions')
        else:
            logger.warning(f'⚠️ user_permissions NOT in cleaned_data!')
            # Check raw POST data
            if 'user_permissions' in request.POST:
                raw_perms = request.POST.getlist('user_permissions')
                logger.info(f'📦 Found in POST data: {len(raw_perms)} permissions')
            else:
                logger.warning(f'⚠️ user_permissions NOT in POST data either!')
        
        # First, let Django handle the default save_related
        super().save_related(request, form, formsets, change)
        
        # Then explicitly ensure user_permissions are set correctly
        if 'user_permissions' in form.cleaned_data:
            selected_permissions = form.cleaned_data['user_permissions']
            
            # Get current permissions count before change
            current_count = obj.user_permissions.count()
            logger.info(f'🔄 Current permissions: {current_count}, New permissions: {selected_permissions.count()}')
            
            # Clear existing permissions and set new ones
            obj.user_permissions.set(selected_permissions)
            
            # Verify the change
            final_count = obj.user_permissions.count()
            logger.info(f'✅ User {obj.username} permissions saved: {final_count} permissions')
            
            if final_count != selected_permissions.count():
                logger.error(f'❌ Permission count mismatch! Expected {selected_permissions.count()}, got {final_count}')
        else:
            # Fallback: Try to get permissions from POST data directly
            if 'user_permissions' in request.POST:
                from django.contrib.auth.models import Permission
                perm_ids = request.POST.getlist('user_permissions')
                logger.info(f'🔧 Fallback: Using POST data directly with {len(perm_ids)} permission IDs')
                
                try:
                    perm_ids = [int(pid) for pid in perm_ids if pid]
                    selected_permissions = Permission.objects.filter(id__in=perm_ids)
                    obj.user_permissions.set(selected_permissions)
                    logger.info(f'✅ Fallback successful: {obj.user_permissions.count()} permissions set')
                except Exception as e:
                    logger.error(f'❌ Fallback failed: {str(e)}')