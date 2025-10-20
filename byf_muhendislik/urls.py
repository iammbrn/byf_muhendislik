from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.sitemaps import Sitemap
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from captcha import urls as captcha_urls
from blog.models import BlogPost
from . import views
from . import admin as custom_admin  # Load custom admin configuration

# Hide Groups from admin (companies use Firm model instead)
admin.site.unregister(Group)


class StaticPagesSitemap(Sitemap):
    """Static pages sitemap"""
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return ['home', 'about', 'services_list', 'contact', 'blog_list']
    
    def location(self, item):
        from django.urls import reverse
        return reverse(item)


class PostSitemap(Sitemap):
    """Blog posts sitemap"""
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        from django.urls import reverse
        return reverse('blog_detail', args=[obj.slug])


# Sitemap dictionary
sitemaps = {
    'static': StaticPagesSitemap,
    'posts': PostSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('hakkimizda/', views.about, name='about'),
    path('hizmetlerimiz/', views.services_list, name='services_list'),
    path('iletisim/', views.contact, name='contact'),
    path('blog/', include('blog.urls')),
    path('hesap/', include('accounts.urls')),
    path('firmalar/', include('firms.urls')),
    path('hizmetler/', include('services.urls')),
    path('dokumanlar/', include('documents.urls')),
    path('captcha/', include(captcha_urls)),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# robots.txt (basic)
urlpatterns += [
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler403 = 'core.views.custom_403'
handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'