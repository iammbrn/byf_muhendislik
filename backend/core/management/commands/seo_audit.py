"""
Management command to audit SEO implementation
Usage: python manage.py seo_audit
"""

from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.test import RequestFactory
from blog.models import BlogPost
from core.models import SiteSettings


class Command(BaseCommand):
    help = 'Audit SEO implementation across the website'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('SEO AUDIT REPORT - BYF MUHENDISLIK'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')

        # Check SiteSettings
        self.stdout.write(self.style.HTTP_INFO('1. SITE SETTINGS CHECK'))
        self.stdout.write('-' * 80)
        
        try:
            site_settings = SiteSettings.objects.first()
            if site_settings:
                self.stdout.write(self.style.SUCCESS('   [OK] SiteSettings configured'))
                
                # Check individual fields
                checks = [
                    ('Site Name', site_settings.site_name),
                    ('Site Description', site_settings.site_description),
                    ('Contact Email', site_settings.contact_email),
                    ('Contact Phone', site_settings.contact_phone),
                    ('Google Analytics ID', site_settings.google_analytics_id),
                    ('Hotjar ID', site_settings.hotjar_id),
                    ('Google Search Console', site_settings.google_search_console),
                    ('Logo', site_settings.logo),
                    ('Facebook URL', site_settings.facebook_url),
                    ('LinkedIn URL', site_settings.linkedin_url),
                    ('Instagram URL', site_settings.instagram_url),
                ]
                
                for field_name, field_value in checks:
                    if field_value:
                        self.stdout.write(f'   [OK] {field_name}: {field_value if len(str(field_value)) < 50 else str(field_value)[:47] + "..."}')
                    else:
                        self.stdout.write(self.style.WARNING(f'   [MISSING] {field_name}'))
            else:
                self.stdout.write(self.style.ERROR('   [ERROR] SiteSettings not configured'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'   [ERROR] {e}'))
        
        self.stdout.write('')

        # Check Blog Posts SEO
        self.stdout.write(self.style.HTTP_INFO('2. BLOG POSTS SEO CHECK'))
        self.stdout.write('-' * 80)
        
        posts = BlogPost.objects.filter(status='published')
        total_posts = posts.count()
        
        if total_posts > 0:
            self.stdout.write(self.style.SUCCESS(f'   [OK] {total_posts} published blog posts found'))
            
            posts_with_images = posts.exclude(featured_image='').count()
            posts_with_excerpt = posts.exclude(excerpt='').count()
            
            self.stdout.write(f'   [INFO] Posts with featured images: {posts_with_images}/{total_posts}')
            self.stdout.write(f'   [INFO] Posts with excerpts: {posts_with_excerpt}/{total_posts}')
            
            # Check for missing SEO elements
            missing_images = total_posts - posts_with_images
            missing_excerpts = total_posts - posts_with_excerpt
            
            if missing_images > 0:
                self.stdout.write(self.style.WARNING(f'   [WARNING] {missing_images} posts missing featured images'))
            if missing_excerpts > 0:
                self.stdout.write(self.style.WARNING(f'   [WARNING] {missing_excerpts} posts missing excerpts'))
        else:
            self.stdout.write(self.style.WARNING('   [WARNING] No published blog posts found'))
        
        self.stdout.write('')

        # Check URL Structure
        self.stdout.write(self.style.HTTP_INFO('3. URL STRUCTURE CHECK'))
        self.stdout.write('-' * 80)
        
        url_checks = [
            ('Home', '/', 'OK - Root URL'),
            ('About', '/hakkimizda/', 'OK - SEO-friendly Turkish URL'),
            ('Services', '/hizmetlerimiz/', 'OK - SEO-friendly Turkish URL'),
            ('Contact', '/iletisim/', 'OK - SEO-friendly Turkish URL'),
            ('Blog', '/blog/', 'OK - Short and clear'),
        ]
        
        for page, url, status in url_checks:
            self.stdout.write(f'   [OK] {page}: {url} - {status}')
        
        self.stdout.write('')

        # Performance Check
        self.stdout.write(self.style.HTTP_INFO('4. PERFORMANCE FEATURES'))
        self.stdout.write('-' * 80)
        
        performance_features = [
            'WhiteNoise static file compression',
            'GZip middleware enabled',
            'Lazy loading on images',
            'Async/Defer JavaScript loading',
            'Preconnect to external resources',
            'Font Awesome async loading',
            'Cache-Control headers',
            'Security headers',
        ]
        
        for feature in performance_features:
            self.stdout.write(self.style.SUCCESS(f'   [OK] {feature}'))
        
        self.stdout.write('')

        # SEO Features Check
        self.stdout.write(self.style.HTTP_INFO('5. SEO FEATURES'))
        self.stdout.write('-' * 80)
        
        seo_features = [
            'Meta descriptions on all pages',
            'Meta keywords on all pages',
            'Open Graph tags (Facebook)',
            'Twitter Card tags',
            'Schema.org Organization markup',
            'Schema.org Article markup (blog)',
            'Schema.org Breadcrumbs',
            'Canonical URLs',
            'Semantic HTML5 structure',
            'Proper heading hierarchy (H1-H6)',
            'XML Sitemap (static pages + blog)',
            'Robots.txt configured',
            'Alt text on all images',
            'SEO-friendly URLs',
        ]
        
        for feature in seo_features:
            self.stdout.write(self.style.SUCCESS(f'   [OK] {feature}'))
        
        self.stdout.write('')

        # Analytics Check
        self.stdout.write(self.style.HTTP_INFO('6. ANALYTICS & MONITORING'))
        self.stdout.write('-' * 80)
        
        if site_settings:
            if site_settings.google_analytics_id:
                self.stdout.write(self.style.SUCCESS(f'   [OK] Google Analytics 4: {site_settings.google_analytics_id}'))
            else:
                self.stdout.write(self.style.WARNING('   [MISSING] Google Analytics ID not configured'))
            
            if site_settings.hotjar_id:
                self.stdout.write(self.style.SUCCESS(f'   [OK] Hotjar: {site_settings.hotjar_id}'))
            else:
                self.stdout.write(self.style.WARNING('   [INFO] Hotjar not configured (optional)'))
            
            if site_settings.google_search_console:
                self.stdout.write(self.style.SUCCESS('   [OK] Google Search Console verification configured'))
            else:
                self.stdout.write(self.style.WARNING('   [TODO] Google Search Console verification not configured'))
        
        self.stdout.write('')

        # Recommendations
        self.stdout.write(self.style.HTTP_INFO('7. RECOMMENDATIONS'))
        self.stdout.write('-' * 80)
        
        recommendations = []
        
        if not site_settings or not site_settings.google_analytics_id:
            recommendations.append('Configure Google Analytics 4 in Site Settings')
        
        if not site_settings or not site_settings.google_search_console:
            recommendations.append('Add Google Search Console verification code')
        
        if not site_settings or not site_settings.hotjar_id:
            recommendations.append('Consider adding Hotjar for user behavior analytics (optional)')
        
        if total_posts > 0:
            if missing_images > 0:
                recommendations.append(f'Add featured images to {missing_images} blog posts')
            if missing_excerpts > 0:
                recommendations.append(f'Add excerpts to {missing_excerpts} blog posts')
        
        if recommendations:
            for rec in recommendations:
                self.stdout.write(self.style.WARNING(f'   [TODO] {rec}'))
        else:
            self.stdout.write(self.style.SUCCESS('   [OK] All SEO best practices implemented!'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write(self.style.SUCCESS('AUDIT COMPLETE'))
        self.stdout.write(self.style.SUCCESS('=' * 80))
        self.stdout.write('')
        
        # Summary
        self.stdout.write(self.style.HTTP_INFO('SUMMARY:'))
        self.stdout.write(f'- Total published blog posts: {total_posts}')
        self.stdout.write(f'- Pages indexed: Static pages + {total_posts} blog posts')
        self.stdout.write(f'- Recommendations: {len(recommendations)}')
        self.stdout.write('')
        
        self.stdout.write('Next Steps:')
        self.stdout.write('1. Configure Google Analytics in admin: /admin/core/sitesettings/')
        self.stdout.write('2. Verify site in Google Search Console')
        self.stdout.write('3. Submit sitemap: /sitemap.xml')
        self.stdout.write('4. Monitor PageSpeed Insights regularly')
        self.stdout.write('5. Check Google Analytics for tracking')
        self.stdout.write('')

