from django.shortcuts import render, get_object_or_404
from django.db.models import F
from .models import BlogPost

def blog_list(request):
    posts = BlogPost.objects.filter(status='published').select_related('author').order_by('-published_at')
    popular_posts = BlogPost.objects.filter(status='published').order_by('-views')[:5]
    
    return render(request, 'blog/blog_list.html', {
        'posts': posts,
        'popular_posts': popular_posts,
    })

def blog_detail(request, slug):
    post = get_object_or_404(
        BlogPost.objects.select_related('author', 'author__profile'),
        slug=slug, 
        status='published'
    )
    
    # Atomic view count increment (prevents race conditions)
    BlogPost.objects.filter(pk=post.pk).update(views=F('views') + 1)
    post.refresh_from_db()
    
    # Get related and similar posts
    related_posts = BlogPost.objects.filter(
        status='published',
        category=post.category
    ).exclude(pk=post.pk).order_by('-published_at')[:3]
    
    similar_posts = BlogPost.objects.filter(
        status='published'
    ).exclude(pk=post.pk).order_by('-views')[:3]
    
    return render(request, 'blog/blog_detail.html', {
        'post': post,
        'related_posts': related_posts,
        'similar_posts': similar_posts,
    })