from django.core.cache import cache
from .models import SiteSettings, ServiceCategory


def site_settings(request):
    """
    Cached context processor for site settings
    Reduces database queries significantly
    """
    # Cache site settings for 1 hour
    settings = cache.get('site_settings')
    if settings is None:
        try:
            settings = SiteSettings.objects.only(
                'site_name', 'site_description', 'contact_email', 'contact_phone',
                'logo', 'facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url',
                'google_analytics_id', 'hotjar_id', 'google_search_console', 'hero_image',
                'about_image'
            ).first()
            cache.set('site_settings', settings, 3600)  # 1 hour cache
        except SiteSettings.DoesNotExist:
            settings = None
            cache.set('site_settings', None, 300)  # Cache "not found" for 5 mins
    
    # Cache service categories for footer (changes rarely)
    service_categories = cache.get('footer_service_categories')
    if service_categories is None:
        service_categories = list(
            ServiceCategory.objects.filter(is_active=True)
            .only('title', 'slug', 'icon', 'subtitle')
            .order_by('order', 'title')
        )
        cache.set('footer_service_categories', service_categories, 7200)  # 2 hours cache
    
    return {
        'site_settings': settings,
        'footer_service_categories': service_categories
    }