"""
Signals for cache invalidation
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import SiteSettings, ServiceCategory


@receiver([post_save, post_delete], sender=SiteSettings)
def clear_site_settings_cache(sender, **kwargs):
    """Clear site settings cache when updated"""
    cache.delete('site_settings')


@receiver([post_save, post_delete], sender=ServiceCategory)
def clear_service_category_cache(sender, **kwargs):
    """Clear service category caches when updated"""
    cache.delete('footer_service_categories')
    cache.delete('services_page_categories')

