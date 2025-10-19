from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'published_at', 'views')
    list_filter = ('status', 'category', 'created_at', 'published_at')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'views', 'unique_id')
    date_hierarchy = 'published_at'
    list_per_page = 20
    
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