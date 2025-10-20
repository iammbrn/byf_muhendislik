from django.contrib import admin
from .models import BlogPost
from core.admin_filters import BlogStatusFilter

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at', 'views')
    list_filter = (BlogStatusFilter, 'category', 'author')
    search_fields = ('title', 'content', 'excerpt', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'views', 'unique_id', 'slug')
    date_hierarchy = 'published_at'  # Date filter at top - removed from list_filter to avoid duplication
    list_per_page = 20
    
    def get_queryset(self, request):
        """Optimize with select_related for ForeignKey fields only"""
        qs = super().get_queryset(request)
        return qs.select_related('author')
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'slug', 'author', 'category', 'status')
        }),
        ('İçerik', {
            'fields': ('excerpt', 'content', 'featured_image')
        }),
        ('Tarihler & İstatistikler', {
            'fields': ('published_at', 'views', 'created_at', 'updated_at', 'unique_id'),
            'classes': ('collapse',)
        }),
    )