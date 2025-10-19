"""
Management command to create database indexes for performance
This creates indexes on frequently queried fields
"""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Create database indexes for improved query performance'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating performance indexes...'))
        self.stdout.write('')
        
        cursor = connection.cursor()
        
        # Blog indexes
        indexes = [
            # BlogPost indexes
            ("CREATE INDEX IF NOT EXISTS idx_blog_status_published ON blog_blogpost(status, published_at DESC) WHERE status = 'published'", 
             "Blog posts by status and date"),
            ("CREATE INDEX IF NOT EXISTS idx_blog_views ON blog_blogpost(views DESC)", 
             "Blog posts by views (popular)"),
            ("CREATE INDEX IF NOT EXISTS idx_blog_category_published ON blog_blogpost(category, published_at DESC) WHERE status = 'published'", 
             "Blog posts by category"),
            
            # Service indexes
            ("CREATE INDEX IF NOT EXISTS idx_service_status ON services_service(status, request_date DESC)", 
             "Services by status"),
            ("CREATE INDEX IF NOT EXISTS idx_service_firm ON services_service(firm_id, status)", 
             "Services by firm"),
            ("CREATE INDEX IF NOT EXISTS idx_service_completion ON services_service(completion_date DESC) WHERE completion_date IS NOT NULL", 
             "Completed services"),
            
            # ServiceRequest indexes
            ("CREATE INDEX IF NOT EXISTS idx_servicerequest_status ON services_servicerequest(status, request_date DESC)", 
             "Service requests by status"),
            ("CREATE INDEX IF NOT EXISTS idx_servicerequest_firm ON services_servicerequest(firm_id, status, request_date DESC)", 
             "Service requests by firm"),
            
            # Document indexes
            ("CREATE INDEX IF NOT EXISTS idx_document_firm ON documents_document(firm_id, upload_date DESC)", 
             "Documents by firm"),
            ("CREATE INDEX IF NOT EXISTS idx_document_service ON documents_document(service_id, upload_date DESC)", 
             "Documents by service"),
            ("CREATE INDEX IF NOT EXISTS idx_document_visible ON documents_document(is_visible_to_firm, upload_date DESC) WHERE is_visible_to_firm = true", 
             "Visible documents"),
            
            # Firm indexes
            ("CREATE INDEX IF NOT EXISTS idx_firm_status ON firms_firm(status, registration_date DESC)", 
             "Firms by status"),
            
            # ContactMessage indexes
            ("CREATE INDEX IF NOT EXISTS idx_contact_status ON core_contactmessage(status, created_at DESC)", 
             "Contact messages by status"),
            
            # TeamMember indexes
            ("CREATE INDEX IF NOT EXISTS idx_team_active ON core_teammember(is_active, \"order\") WHERE is_active = true", 
             "Active team members"),
            
            # ServiceCategory indexes
            ("CREATE INDEX IF NOT EXISTS idx_servicecategory_active ON core_servicecategory(is_active, \"order\") WHERE is_active = true", 
             "Active service categories"),
        ]
        
        created_count = 0
        for sql, description in indexes:
            try:
                cursor.execute(sql)
                self.stdout.write(self.style.SUCCESS(f'  [OK] {description}'))
                created_count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  [SKIP] {description}: {str(e)[:50]}'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Created {created_count}/{len(indexes)} indexes'))
        self.stdout.write('')
        self.stdout.write('These indexes will significantly improve:')
        self.stdout.write('  - Dashboard load times')
        self.stdout.write('  - Blog page rendering')
        self.stdout.write('  - Service list filtering')
        self.stdout.write('  - Document queries')
        self.stdout.write('')

