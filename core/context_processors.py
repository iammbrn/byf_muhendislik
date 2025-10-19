from .models import SiteSettings, ServiceCategory

def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
    except SiteSettings.DoesNotExist:
        settings = None
    
    # Tüm aktif hizmet kategorilerini footer için ekle
    service_categories = ServiceCategory.objects.filter(is_active=True).order_by('order', 'title')
    
    return {
        'site_settings': settings,
        'footer_service_categories': service_categories
    }