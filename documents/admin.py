from django.contrib import admin
from .models import Document
from core.admin_filters import FirmVisibilityFilter, DocumentTypeFilter

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'firm', 'service', 'document_type', 'upload_date', 'uploaded_by', 'download_count', 'is_visible_to_firm')
    list_filter = (DocumentTypeFilter, FirmVisibilityFilter, 'firm')
    search_fields = ('name', 'firm__name', 'description', 'service__name')
    readonly_fields = ('upload_date', 'unique_id', 'download_count')
    date_hierarchy = 'upload_date'  # Date filter at top - removed from list_filter to avoid duplication
    
    def get_queryset(self, request):
        """Optimize with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('firm', 'service', 'uploaded_by')
    
    fieldsets = (
        ('Doküman Bilgileri', {
            'fields': ('name', 'firm', 'service', 'file', 'document_type', 'description')
        }),
        ('Görünürlük', {
            'fields': ('is_visible_to_firm',)
        }),
        ('Sistem Bilgileri', {
            'fields': ('upload_date', 'uploaded_by', 'download_count', 'unique_id'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_module_permission(self, request):
        """Allow staff users with permissions to access this module"""
        return request.user.is_superuser or (request.user.is_staff and (
            request.user.has_perm('documents.view_document') or
            request.user.has_perm('documents.add_document') or
            request.user.has_perm('documents.change_document')
        ))
    
    def has_view_permission(self, request, obj=None):
        """Allow viewing for users with view or change permission"""
        return request.user.is_superuser or request.user.has_perm('documents.view_document') or request.user.has_perm('documents.change_document')
    
    def has_add_permission(self, request):
        """Allow adding for users with add permission"""
        return request.user.is_superuser or request.user.has_perm('documents.add_document')
    
    def has_change_permission(self, request, obj=None):
        """Allow editing for users with change permission"""
        return request.user.is_superuser or request.user.has_perm('documents.change_document')
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers"""
        return request.user.is_superuser