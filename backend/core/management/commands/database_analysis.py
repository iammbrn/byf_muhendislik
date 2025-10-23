"""
Database structure analysis and optimization report
Usage: python manage.py database_analysis
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.apps import apps


class Command(BaseCommand):
    help = 'Analyze database structure and provide optimization report'

    def handle(self, *args, **options):
        self.stdout.write('=' * 80)
        self.stdout.write('DATABASE STRUCTURE ANALYSIS - BYF MUHENDISLIK')
        self.stdout.write('=' * 80)
        self.stdout.write('')

        self.check_indexes()
        self.check_constraints()
        self.check_table_sizes()
        self.check_model_optimizations()
        self.check_relationships()

        self.stdout.write('')
        self.stdout.write('=' * 80)
        self.stdout.write('ANALYSIS COMPLETE')
        self.stdout.write('=' * 80)

    def check_indexes(self):
        self.stdout.write('[DATABASE INDEXES]')
        self.stdout.write('-' * 80)
        
        cursor = connection.cursor()
        
        # Count indexes
        cursor.execute("""
            SELECT 
                schemaname,
                COUNT(*) as index_count
            FROM pg_indexes
            WHERE schemaname = 'public'
            GROUP BY schemaname
        """)
        
        for schema, count in cursor.fetchall():
            self.stdout.write(f'  Total indexes in {schema}: {count}')
        
        # Custom indexes
        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_indexes
            WHERE schemaname = 'public'
            AND (indexname LIKE 'idx_%' OR indexname LIKE '%_idx')
        """)
        
        custom_count = cursor.fetchone()[0]
        self.stdout.write(f'  Custom performance indexes: {custom_count}')
        
        self.stdout.write('')

    def check_constraints(self):
        self.stdout.write('[DATABASE CONSTRAINTS]')
        self.stdout.write('-' * 80)
        
        cursor = connection.cursor()
        
        # Check constraints
        cursor.execute("""
            SELECT 
                conname,
                contype
            FROM pg_constraint
            WHERE connamespace = 'public'::regnamespace
            AND contype IN ('c', 'u', 'f', 'p')
        """)
        
        constraint_types = {'c': 0, 'u': 0, 'f': 0, 'p': 0}
        for name, ctype in cursor.fetchall():
            constraint_types[ctype] = constraint_types.get(ctype, 0) + 1
        
        self.stdout.write(f'  Check constraints: {constraint_types["c"]}')
        self.stdout.write(f'  Unique constraints: {constraint_types["u"]}')
        self.stdout.write(f'  Foreign keys: {constraint_types["f"]}')
        self.stdout.write(f'  Primary keys: {constraint_types["p"]}')
        
        self.stdout.write('')

    def check_table_sizes(self):
        self.stdout.write('[TABLE SIZES & STATISTICS]')
        self.stdout.write('-' * 80)
        
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
                pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS indexes_size
            FROM pg_tables
            WHERE schemaname = 'public'
            AND tablename NOT LIKE 'django_%'
            AND tablename NOT LIKE 'auth_%'
            AND tablename NOT LIKE 'captcha_%'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10
        """)
        
        self.stdout.write('  Top 10 tables by size:')
        for schema, table, total_size, table_size, index_size in cursor.fetchall():
            self.stdout.write(f'    {table:35} Total: {total_size:10} (Data: {table_size}, Indexes: {index_size})')
        
        self.stdout.write('')

    def check_model_optimizations(self):
        self.stdout.write('[MODEL-LEVEL OPTIMIZATIONS]')
        self.stdout.write('-' * 80)
        
        # Get all app models
        app_labels = ['accounts', 'firms', 'services', 'documents', 'blog', 'core']
        
        for app_label in app_labels:
            app_models = apps.get_app_config(app_label).get_models()
            
            for model in app_models:
                if model._meta.proxy:
                    continue
                    
                has_indexes = len(model._meta.indexes) > 0
                has_ordering = len(model._meta.ordering) > 0
                has_db_table_comment = hasattr(model._meta, 'db_table_comment')
                
                status = '[OK]' if has_indexes or has_ordering else '[INFO]'
                index_count = len(model._meta.indexes)
                
                self.stdout.write(
                    f'  {status} {app_label}.{model.__name__:25} '
                    f'Indexes: {index_count:2} | '
                    f'Ordering: {"Yes" if has_ordering else "No":3} | '
                    f'Comment: {"Yes" if has_db_table_comment else "No":3}'
                )
        
        self.stdout.write('')

    def check_relationships(self):
        self.stdout.write('[FOREIGN KEY RELATIONSHIPS]')
        self.stdout.write('-' * 80)
        
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT 
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name,
                rc.delete_rule
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
              AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
              AND ccu.table_schema = tc.table_schema
            JOIN information_schema.referential_constraints AS rc
              ON rc.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema = 'public'
            AND tc.table_name NOT LIKE 'django_%'
            AND tc.table_name NOT LIKE 'auth_%'
            ORDER BY tc.table_name, kcu.column_name
        """)
        
        relationships = cursor.fetchall()
        self.stdout.write(f'  Total foreign key relationships: {len(relationships)}')
        
        # Group by delete rule
        delete_rules = {}
        for row in relationships:
            rule = row[4]
            delete_rules[rule] = delete_rules.get(rule, 0) + 1
        
        for rule, count in delete_rules.items():
            self.stdout.write(f'    {rule:20} {count} relationships')
        
        self.stdout.write('')
        
        # Show key relationships
        self.stdout.write('  Key relationships:')
        for table, column, fk_table, fk_column, delete_rule in relationships[:15]:
            self.stdout.write(f'    {table:30} {column:20} -> {fk_table}({fk_column}) [{delete_rule}]')
        
        if len(relationships) > 15:
            self.stdout.write(f'    ... and {len(relationships) - 15} more')
        
        self.stdout.write('')

