from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone

from .models import Service, ServiceRequest
from core.admin_filters import ServiceStatusFilter, ServiceTypeFilter, PriorityFilter


# Status badge colors - shared across admin classes
STATUS_COLORS = {
    'pending': '#ffc107',
    'approved': '#10b981',
    'rejected': '#ef4444',
    'in_progress': '#3b82f6',
    'completed': '#10b981',
}


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'firm', 'service_type', 'status', 'request_date', 'assigned_admin')
    list_filter = (ServiceTypeFilter, ServiceStatusFilter, 'firm', 'assigned_admin')
    search_fields = ('name', 'firm__name', 'description')
    readonly_fields = ('request_date', 'unique_id')
    date_hierarchy = 'request_date'  # Date filter at top - request_date not in list_filter
    
    def get_queryset(self, request):
        """Show only completed services"""
        return super().get_queryset(request).filter(status='completed').select_related('firm', 'assigned_admin')

@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'firm', 'service_type', 'priority', 'status_badge', 'request_date', 'action_buttons')
    list_filter = (ServiceStatusFilter, ServiceTypeFilter, PriorityFilter, 'firm')
    search_fields = ('title', 'firm__name', 'description', 'tracking_code')
    readonly_fields = ('request_date', 'updated_at', 'unique_id', 'tracking_code')
    date_hierarchy = 'request_date'  # Date filter at top - removed from list_filter to avoid duplication
    fieldsets = (
        ('Talep Bilgileri', {
            'fields': ('firm', 'service_type', 'title', 'description', 'priority', 'requested_completion_date', 'tracking_code')
        }),
        ('Durum', {
            'fields': ('status', 'admin_response', 'responded_by')
        }),
        ('Sistem Bilgileri', {
            'fields': ('request_date', 'updated_at', 'unique_id'),
            'classes': ('collapse',)
        }),
    )
    actions = ['approve_requests', 'reject_requests', 'delete_selected']
    
    def has_module_permission(self, request):
        """Allow both superusers and staff to access this module"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_view_permission(self, request, obj=None):
        """Allow viewing for superusers and staff"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_change_permission(self, request, obj=None):
        """Allow editing for superusers and staff"""
        return request.user.is_superuser or request.user.is_staff
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers"""
        return request.user.is_superuser
    
    def get_queryset(self, request):
        """Show only pending and approved requests"""
        return super().get_queryset(request).filter(status__in=['pending', 'approved']).select_related('firm', 'responded_by')
    
    def status_badge(self, obj):
        return format_html(
            '<span style="background: {}; color: white; padding: 0.25rem 0.75rem; border-radius: 0.5rem; font-weight: 600; font-size: 0.75rem;">{}</span>',
            STATUS_COLORS.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Durum'
    
    def action_buttons(self, obj):
        if obj.status == 'pending':
            approve_url = reverse('admin:services_servicerequest_change', args=[obj.pk])
            return format_html(
                '<a class="button" style="background: #10b981; color: white; padding: 0.5rem 1rem; border-radius: 0.5rem; text-decoration: none; margin-right: 0.5rem;" href="{}">Yönet</a>',
                approve_url
            )
        return '-'
    action_buttons.short_description = 'İşlemler'
    
    def approve_requests(self, request, queryset):
        updated = 0
        created_services = 0
        for service_request in queryset:
            if service_request.status == 'pending':
                service_request.status = 'approved'
                service_request.responded_by = request.user
                service_request.save()
                updated += 1
                
                # Service oluştur
                if not Service.objects.filter(firm=service_request.firm, name__icontains=service_request.title).exists():
                    Service.objects.create(
                        name=service_request.title,
                        service_type=service_request.service_type,
                        description=service_request.description,
                        firm=service_request.firm,
                        status='in_progress',
                        assigned_admin=request.user,
                    )
                    created_services += 1
        
        self.message_user(request, f'✅ {updated} talep onaylandı ve {created_services} hizmet oluşturuldu.')
    approve_requests.short_description = '✅ Seçili talepleri onayla'
    
    def reject_requests(self, request, queryset):
        updated = queryset.update(status='rejected', responded_by=request.user)
        self.message_user(request, f'{updated} talep reddedildi.')
    reject_requests.short_description = '❌ Seçili talepleri reddet'
    
    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            old_obj = ServiceRequest.objects.get(pk=obj.pk)
            old_status = old_obj.status
            
            if 'status' in form.changed_data:
                obj.responded_by = request.user
            
        super().save_model(request, obj, form, change)
        
        # Auto-update related Service on status change
        if change and old_status and old_status != obj.status:
            # İlgili Service'i bul veya oluştur
            service = Service.objects.filter(firm=obj.firm, name__icontains=obj.title).first()
            
            # APPROVED veya IN_PROGRESS: Service oluştur/güncelle
            if obj.status in ['approved', 'in_progress']:
                if not service:
                    # Yeni Service oluştur
                    service = Service.objects.create(
                        name=obj.title,
                        service_type=obj.service_type,
                        description=obj.description,
                        firm=obj.firm,
                        status='in_progress',
                        assigned_admin=request.user,
                    )
                    self.message_user(request, f'✅ Hizmet oluşturuldu ve "Devam Ediyor" olarak işaretlendi: {service.name}', level='SUCCESS')
                else:
                    # Mevcut Service'i güncelle
                    if service.status != 'in_progress':
                        service.status = 'in_progress'
                        service.assigned_admin = request.user
                        service.save(update_fields=['status', 'assigned_admin'])
                        self.message_user(request, f'✅ Hizmet "Devam Ediyor" olarak güncellendi: {service.name}', level='SUCCESS')
            
            # COMPLETED: Mark service as completed
            elif obj.status == 'completed':
                if service and service.status != 'completed':
                    service.status = 'completed'
                    if not service.completion_date:
                        service.completion_date = timezone.now().date()
                    service.save(update_fields=['status', 'completion_date'])
                    self.message_user(request, f'✅ Hizmet "Tamamlandı" olarak işaretlendi: {service.name}', level='SUCCESS')