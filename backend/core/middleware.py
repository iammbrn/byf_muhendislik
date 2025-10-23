"""
Core middleware for performance and SEO optimization
"""

from django.utils.cache import patch_cache_control


class CacheControlMiddleware:
    """
    Add cache control headers for better performance
    """
    
    # Pages that should have cache headers
    CACHEABLE_PATHS = [
        '/',
        '/hakkimizda/',
        '/hizmetlerimiz/',
        '/iletisim/',
        '/blog/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add cache headers for public pages
        if request.path in self.CACHEABLE_PATHS or request.path.startswith('/blog/'):
            # Cache for 1 hour for public pages
            if response.status_code == 200 and not request.user.is_authenticated:
                patch_cache_control(
                    response,
                    public=True,
                    max_age=3600,  # 1 hour
                    s_maxage=3600,
                )
        
        # No cache for authenticated pages
        elif request.user.is_authenticated:
            patch_cache_control(
                response,
                private=True,
                no_cache=True,
                no_store=True,
                must_revalidate=True,
            )
        
        return response


class SecurityHeadersMiddleware:
    """
    Add additional security headers
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add performance hints
        response['X-DNS-Prefetch-Control'] = 'on'
        
        return response

