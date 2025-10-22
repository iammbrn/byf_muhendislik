from django.contrib import admin
from .models import SiteSettings, ActivityLog, ProvisionedCredential, ContactMessage, ServiceCategory, TeamMember
from django.utils.html import format_html
from django.utils import timezone
from .admin_filters import AdminTypeFilter, ActiveStatusFilter, ContactMessageStatusFilter


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "contact_email", "contact_phone", "updated_at")
    search_fields = ("site_name", "contact_email", "contact_phone")
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('site_name', 'site_description')
        }),
        ('İletişim Bilgileri', {
            'fields': ('contact_email', 'contact_phone', 'address', 'whatsapp_number')
        }),
        ('Görseller', {
            'fields': ('logo', 'favicon', 'hero_image', 'about_image'),
            'description': 'Logo, favicon ve sayfa görsellerini buradan güncelleyebilirsiniz'
        }),
        ('Sosyal Medya', {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url'),
            'classes': ('collapse',)
        }),
        ('Gelişmiş', {
            'fields': ('google_analytics_id',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "message_preview", "created_at")
    list_filter = ("action", "user__user_type")
    search_fields = ("user__username", "message")
    date_hierarchy = 'created_at'  # Date filter at top - removed from list_filter to avoid duplication
    readonly_fields = ('user', 'action', 'message', 'created_at')
    
    def get_queryset(self, request):
        """Optimize with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user')
    
    def message_preview(self, obj):
        """Show truncated message"""
        if obj.message and len(obj.message) > 50:
            return obj.message[:50] + '...'
        return obj.message or '-'
    message_preview.short_description = 'Mesaj'


@admin.register(ProvisionedCredential)
class ProvisionedCredentialAdmin(admin.ModelAdmin):
    list_display = ("username", "user", "is_admin", "created_at")
    list_filter = (AdminTypeFilter,)
    search_fields = ("username", "user__username", "user__email")
    readonly_fields = ("username", "password_plain", "is_admin", "created_at")
    date_hierarchy = 'created_at'  # Date filter at top - removed from list_filter to avoid duplication
    
    def get_queryset(self, request):
        """Optimize with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name_display', 'email', 'phone', 'subject', 'status_badge', 'created_at')
    list_filter = (ContactMessageStatusFilter, 'created_at')
    search_fields = ('name', 'surname', 'email', 'phone', 'subject', 'message')
    readonly_fields = ('name', 'surname', 'email', 'phone', 'subject', 'message', 'created_at')
    actions = ['mark_as_read', 'mark_as_replied', 'archive_messages', 'delete_selected']
    
    fieldsets = (
        ('Gönderen Bilgileri', {
            'fields': ('name', 'surname', 'email', 'phone')
        }),
        ('Mesaj', {
            'fields': ('subject', 'message', 'created_at')
        }),
        ('Yönetim', {
            'fields': ('status', 'response_note', 'responded_at')
        }),
    )
    
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'Ad Soyad'
    
    def status_badge(self, obj):
        colors = {
            'new': '#f59e0b',
            'read': '#3b82f6',
            'replied': '#10b981',
            'archived': '#6c757d',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 0.25rem 0.75rem; border-radius: 0.5rem; font-weight: 600; font-size: 0.75rem;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(status='read')
        self.message_user(request, f'{updated} mesaj okundu olarak işaretlendi.')
    mark_as_read.short_description = '👁️ Seçili mesajları okundu olarak işaretle'
    
    def mark_as_replied(self, request, queryset):
        updated = queryset.update(status='replied', responded_at=timezone.now())
        self.message_user(request, f'{updated} mesaj yanıtlandı olarak işaretlendi.')
    mark_as_replied.short_description = '✉️ Seçili mesajları yanıtlandı olarak işaretle'
    
    def archive_messages(self, request, queryset):
        updated = queryset.update(status='archived')
        self.message_user(request, f'{updated} mesaj arşivlendi.')
    archive_messages.short_description = '📦 Seçili mesajları arşivle'
    
    def has_module_permission(self, request):
        """Allow staff users with permissions to access this module"""
        return request.user.is_superuser or (request.user.is_staff and (
            request.user.has_perm('core.view_contactmessage') or
            request.user.has_perm('core.change_contactmessage')
        ))
    
    def has_view_permission(self, request, obj=None):
        """Allow viewing for users with view or change permission"""
        return request.user.is_superuser or request.user.has_perm('core.view_contactmessage') or request.user.has_perm('core.change_contactmessage')
    
    def has_add_permission(self, request):
        """Contact messages cannot be added via admin"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Allow editing for users with change permission"""
        return request.user.is_superuser or request.user.has_perm('core.change_contactmessage')
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers"""
        return request.user.is_superuser
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status == 'replied':
            obj.responded_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'updated_at')
    list_filter = (ActiveStatusFilter, 'created_at')
    search_fields = ('title', 'subtitle', 'description')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'icon', 'subtitle', 'is_active', 'order')
        }),
        ('İçerik', {
            'fields': ('description', 'scope_items', 'features')
        }),
        ('Süreç & Standartlar', {
            'fields': ('process_steps', 'standards'),
            'classes': ('collapse',),
            'description': 'Süreç Adımları formatı: [{"title": "İlk Görüşme", "description": "Müşteri ile detaylı görüşme yapılır"}, {"title": "Keşif", "description": "Saha incelemesi gerçekleştirilir"}]'
        }),
    )
    
    class Media:
        # CSS already loaded globally via base_site.html - no need to duplicate
        js = ('admin/js/json_editor.js',)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'image_preview', 'order', 'is_active', 'updated_at')
    list_filter = (ActiveStatusFilter, 'created_at')
    search_fields = ('name', 'title', 'bio')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('name', 'slug', 'title', 'image', 'is_active', 'order')
        }),
        ('İçerik', {
            'fields': ('bio',)
        }),
        ('İletişim', {
            'fields': ('email', 'phone', 'linkedin_url'),
            'classes': ('collapse',)
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 50%;" />',
                obj.image.url
            )
        return '-'
    image_preview.short_description = 'Önizleme'
