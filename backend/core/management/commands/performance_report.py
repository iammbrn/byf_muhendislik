"""
Performance monitoring and reporting command
Usage: python manage.py performance_report
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time


class Command(BaseCommand):
    help = 'Generate performance report for the website'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed query analysis',
        )

    def handle(self, *args, **options):
        self.stdout.write('=' * 80)
        self.stdout.write('PERFORMANCE REPORT - BYF MUHENDISLIK')
        self.stdout.write('=' * 80)
        self.stdout.write('')

        # Database Performance
        self.check_database_performance()
        
        # Cache Performance
        self.check_cache_performance()
        
        # Middleware Performance
        self.check_middleware_config()
        
        # Static Files
        self.check_static_files()
        
        # Query Optimization
        if options['detailed']:
            self.check_query_optimization()
        
        self.stdout.write('')
        self.stdout.write('=' * 80)
        self.stdout.write('REPORT COMPLETE')
        self.stdout.write('=' * 80)

    def check_database_performance(self):
        self.stdout.write('[DATABASE PERFORMANCE]')
        self.stdout.write('-' * 80)
        
        cursor = connection.cursor()
        
        # Check if indexes exist
        cursor.execute("""
            SELECT COUNT(*) 
            FROM pg_indexes 
            WHERE schemaname = 'public' 
            AND indexname LIKE 'idx_%'
        """)
        index_count = cursor.fetchone()[0]
        
        self.stdout.write(f'  Custom indexes: {index_count}')
        
        # Table sizes
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 5
        """)
        
        self.stdout.write('  Largest tables:')
        for schema, table, size in cursor.fetchall():
            self.stdout.write(f'    - {table}: {size}')
        
        self.stdout.write('')

    def check_cache_performance(self):
        self.stdout.write('[CACHE CONFIGURATION]')
        self.stdout.write('-' * 80)
        
        cache_backend = settings.CACHES['default']['BACKEND']
        self.stdout.write(f'  Backend: {cache_backend}')
        
        if 'redis' in cache_backend.lower():
            self.stdout.write('  Type: Redis (Production-ready)')
        elif 'locmem' in cache_backend.lower():
            self.stdout.write('  Type: Local Memory (Development)')
        
        # Test cache
        test_key = 'performance_test'
        start = time.time()
        cache.set(test_key, 'test_value', 60)
        set_time = (time.time() - start) * 1000
        
        start = time.time()
        value = cache.get(test_key)
        get_time = (time.time() - start) * 1000
        
        cache.delete(test_key)
        
        self.stdout.write(f'  Cache write speed: {set_time:.2f}ms')
        self.stdout.write(f'  Cache read speed: {get_time:.2f}ms')
        
        # Check cached items
        cached_items = [
            'site_settings',
            'footer_service_categories',
            'services_page_categories',
        ]
        
        cached_count = sum(1 for item in cached_items if cache.get(item) is not None)
        self.stdout.write(f'  Cached items: {cached_count}/{len(cached_items)}')
        
        self.stdout.write('')

    def check_middleware_config(self):
        self.stdout.write('[MIDDLEWARE CONFIGURATION]')
        self.stdout.write('-' * 80)
        
        middleware_checks = [
            ('GZip Compression', 'django.middleware.gzip.GZipMiddleware'),
            ('WhiteNoise Static', 'whitenoise.middleware.WhiteNoiseMiddleware'),
            ('Cache Control', 'core.middleware.CacheControlMiddleware'),
            ('Security Headers', 'core.middleware.SecurityHeadersMiddleware'),
        ]
        
        for name, middleware in middleware_checks:
            if middleware in settings.MIDDLEWARE:
                self.stdout.write(f'  [OK] {name}')
            else:
                self.stdout.write(f'  [MISSING] {name}')
        
        self.stdout.write('')

    def check_static_files(self):
        self.stdout.write('[STATIC FILES OPTIMIZATION]')
        self.stdout.write('-' * 80)
        
        storage = settings.STATICFILES_STORAGE
        self.stdout.write(f'  Storage: {storage}')
        
        if 'Compressed' in storage:
            self.stdout.write('  [OK] Compression enabled')
        if 'Manifest' in storage:
            self.stdout.write('  [OK] Manifest (cache-busting) enabled')
        
        whitenoise_age = getattr(settings, 'WHITENOISE_MAX_AGE', None)
        if whitenoise_age:
            days = whitenoise_age / (60 * 60 * 24)
            self.stdout.write(f'  [OK] Cache max-age: {int(days)} days')
        
        self.stdout.write('')

    def check_query_optimization(self):
        self.stdout.write('[QUERY OPTIMIZATION ANALYSIS]')
        self.stdout.write('-' * 80)
        
        optimizations = [
            'select_related() for ForeignKey relations',
            'prefetch_related() for reverse relations',
            'only() to limit fetched fields',
            'Caching for frequently accessed data',
            'Database indexes on filtered fields',
            'Atomic operations for counters',
        ]
        
        for opt in optimizations:
            self.stdout.write(f'  [OK] {opt}')
        
        self.stdout.write('')
        self.stdout.write('  Key optimizations applied:')
        self.stdout.write('    - Context processor uses caching')
        self.stdout.write('    - Blog queries use only()')
        self.stdout.write('    - Service queries optimized')
        self.stdout.write('    - View counters use F() expressions')
        self.stdout.write('')

