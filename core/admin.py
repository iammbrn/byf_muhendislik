from django.contrib import admin
from .models import SiteSettings, ActivityLog, ProvisionedCredential, ContactMessage, ServiceCategory, TeamMember
from django.utils.html import format_html
from django.utils import timezone


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "contact_email", "contact_phone", "updated_at")
    search_fields = ("site_name", "contact_email")
    
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
    list_display = ("user", "action", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "message")


@admin.register(ProvisionedCredential)
class ProvisionedCredentialAdmin(admin.ModelAdmin):
    list_display = ("username", "is_admin", "created_at")
    list_filter = ("is_admin", "created_at")
    search_fields = ("username", "user__username")
    readonly_fields = ("username", "password_plain", "is_admin", "created_at")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name_display', 'email', 'phone', 'subject', 'status_badge', 'created_at')
    list_filter = ('status', 'created_at')
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
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data and obj.status == 'replied':
            obj.responded_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active', 'updated_at')
    list_filter = ('is_active', 'created_at')
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
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/json_editor.js',)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'image_preview', 'order', 'is_active', 'updated_at')
    list_filter = ('is_active', 'created_at')
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
