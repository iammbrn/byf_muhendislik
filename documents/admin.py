from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'firm', 'service', 'document_type', 'upload_date', 'uploaded_by', 'download_count', 'is_visible_to_firm')
    list_filter = ('document_type', 'upload_date', 'is_visible_to_firm', 'service')
    search_fields = ('name', 'firm__name', 'description', 'service__name')
    readonly_fields = ('upload_date', 'unique_id', 'download_count')
    
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