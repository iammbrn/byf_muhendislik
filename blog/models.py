from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
import uuid

class BlogPost(models.Model):
    class Category(models.TextChoices):
        GENERAL = 'general', 'Genel'
        NEWS = 'news', 'Haber'
        TIPS = 'tips', 'İpucu'

    STATUS_CHOICES = (
        ('draft', 'Taslak'),
        ('published', 'Yayında'),
        ('archived', 'Arşivlendi'),
    )
    
    title = models.CharField(max_length=255, verbose_name='Başlık')
    slug = models.SlugField(max_length=300, unique=True, verbose_name='SEO URL')
    content = models.TextField(verbose_name='İçerik')
    excerpt = models.TextField(blank=True, verbose_name='Özet')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Yazar')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Durum')
    category = models.CharField(max_length=32, choices=Category.choices, default=Category.GENERAL, verbose_name='Kategori')
    featured_image = models.ImageField(upload_to='blog/', blank=True, null=True, verbose_name='Kapak Görseli')
    views = models.PositiveIntegerField(default=0, verbose_name='Görüntülenme')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='Yayınlanma Tarihi')
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    class Meta:
        verbose_name = 'Blog Yazısı'
        verbose_name_plural = 'Blog Yazıları'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-published_at'], name='blog_published_date_idx'),
            models.Index(fields=['status', '-published_at'], name='blog_status_pub_idx'),
            models.Index(fields=['-views'], name='blog_views_idx'),
            models.Index(fields=['category', '-published_at'], name='blog_cat_pub_idx'),
            models.Index(fields=['author', '-published_at'], name='blog_author_pub_idx'),
        ]
        db_table_comment = 'Blog yazıları - SEO optimized content'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            num = 1
            while BlogPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{num}"
                num += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog_detail', kwargs={'slug': self.slug})