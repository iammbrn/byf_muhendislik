"""
Custom admin filters for better UX
Provides clear, descriptive labels with clean, modern design
"""
from django.contrib import admin


class ActiveStatusFilter(admin.SimpleListFilter):
    """Filter for is_active field with clear labels"""
    title = 'Durum'
    parameter_name = 'is_active'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Aktif'),
            ('0', 'Pasif'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_active=True)
        if self.value() == '0':
            return queryset.filter(is_active=False)
        return queryset


class AdminTypeFilter(admin.SimpleListFilter):
    """Filter for is_admin field with clear labels"""
    title = 'Kullanıcı Tipi'
    parameter_name = 'is_admin'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Yönetici'),
            ('0', 'Firma'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_admin=True)
        if self.value() == '0':
            return queryset.filter(is_admin=False)
        return queryset


class FirmVisibilityFilter(admin.SimpleListFilter):
    """Filter for is_visible_to_firm field with clear labels"""
    title = 'Görünürlük'
    parameter_name = 'is_visible_to_firm'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Firmaya Görünür'),
            ('0', 'Gizli'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_visible_to_firm=True)
        if self.value() == '0':
            return queryset.filter(is_visible_to_firm=False)
        return queryset


class SuperuserFilter(admin.SimpleListFilter):
    """Filter for is_superuser field with clear labels"""
    title = 'Yetki Seviyesi'
    parameter_name = 'is_superuser'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Süper Yönetici'),
            ('0', 'Standart Yönetici'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_superuser=True)
        if self.value() == '0':
            return queryset.filter(is_superuser=False)
        return queryset


class StaffStatusFilter(admin.SimpleListFilter):
    """Filter for is_staff field with clear labels"""
    title = 'Personel Durumu'
    parameter_name = 'is_staff'

    def lookups(self, request, model_admin):
        return (
            ('1', 'Personel'),
            ('0', 'Personel Değil'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(is_staff=True)
        if self.value() == '0':
            return queryset.filter(is_staff=False)
        return queryset


class FirmStatusFilter(admin.SimpleListFilter):
    """Filter for firm status with clear labels"""
    title = 'Firma Durumu'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('active', 'Aktif'),
            ('inactive', 'Pasif'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class BlogStatusFilter(admin.SimpleListFilter):
    """Filter for blog post status with clear labels"""
    title = 'Yayın Durumu'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('published', 'Yayında'),
            ('draft', 'Taslak'),
            ('archived', 'Arşivlendi'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class ServiceStatusFilter(admin.SimpleListFilter):
    """Filter for service status with clear labels"""
    title = 'Hizmet Durumu'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('pending', 'Beklemede'),
            ('approved', 'Onaylandı'),
            ('in_progress', 'Devam Ediyor'),
            ('completed', 'Tamamlandı'),
            ('rejected', 'Reddedildi'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class ContactMessageStatusFilter(admin.SimpleListFilter):
    """Filter for contact message status with clear labels"""
    title = 'Mesaj Durumu'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('new', 'Yeni'),
            ('read', 'Okundu'),
            ('replied', 'Yanıtlandı'),
            ('archived', 'Arşivlendi'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset


class DocumentTypeFilter(admin.SimpleListFilter):
    """Filter for document type with clear labels"""
    title = 'Doküman Türü'
    parameter_name = 'document_type'

    def lookups(self, request, model_admin):
        return (
            ('contract', 'Sözleşme'),
            ('report', 'Rapor'),
            ('certificate', 'Sertifika'),
            ('invoice', 'Fatura'),
            ('other', 'Diğer'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(document_type=self.value())
        return queryset


class ServiceTypeFilter(admin.SimpleListFilter):
    """Filter for service type with clear labels"""
    title = 'Hizmet Türü'
    parameter_name = 'service_type'

    def lookups(self, request, model_admin):
        return (
            ('electrical', 'Elektrik Projesi'),
            ('mechanical', 'Mekanik Proje'),
            ('plumbing', 'Tesisat Projesi'),
            ('fire', 'Yangın Projesi'),
            ('consultation', 'Danışmanlık'),
            ('other', 'Diğer'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(service_type=self.value())
        return queryset


class PriorityFilter(admin.SimpleListFilter):
    """Filter for priority with clear labels"""
    title = 'Öncelik'
    parameter_name = 'priority'

    def lookups(self, request, model_admin):
        return (
            ('low', 'Düşük'),
            ('medium', 'Orta'),
            ('high', 'Yüksek'),
            ('urgent', 'Acil'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(priority=self.value())
        return queryset

