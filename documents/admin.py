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