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


class PostSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return BlogPost.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

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
    path('sitemap.xml', sitemap, {'sitemaps': {'posts': PostSitemap}}, name='django.contrib.sitemaps.views.sitemap'),
]

# robots.txt (basic)
urlpatterns += [
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'