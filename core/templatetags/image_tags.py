"""
Custom template tags for image optimization
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def responsive_image(image_field, alt_text=''):
    """
    Generate responsive image tag with srcset for better performance
    Usage: {{ post.featured_image|responsive_image:"Alt text" }}
    """
    if not image_field:
        return ''
    
    # Get image URL
    image_url = image_field.url
    
    # Generate responsive image HTML
    # Note: For production, you'd generate multiple sizes server-side
    # For now, we use CSS and browser native optimization
    html = f'''<img src="{image_url}" 
                    alt="{alt_text}" 
                    loading="lazy" 
                    decoding="async"
                    class="responsive-img"
                    style="max-width: 100%; height: auto;">'''
    
    return mark_safe(html)


@register.simple_tag
def responsive_bg_image(image_field, css_class=''):
    """
    Generate div with background image for better responsive control
    Usage: {% responsive_bg_image post.featured_image "hero-bg" %}
    """
    if not image_field:
        return ''
    
    image_url = image_field.url
    style = f'background-image: url({image_url});'
    
    return mark_safe(
        f'<div class="{css_class} responsive-bg" style="{style}"></div>'
    )


@register.filter
def image_dimensions(image_field):
    """
    Get image dimensions if available
    Usage: {{ post.featured_image|image_dimensions }}
    Returns: tuple (width, height) or None
    """
    if not image_field:
        return None
    
    try:
        return (image_field.width, image_field.height)
    except:
        return None


@register.inclusion_tag('core/responsive_image.html')
def render_responsive_image(image, alt='', sizes='100vw', css_class=''):
    """
    Render a fully optimized responsive image
    Usage: {% render_responsive_image post.featured_image "Alt text" sizes="(max-width: 768px) 100vw, 50vw" %}
    """
    return {
        'image': image,
        'alt': alt,
        'sizes': sizes,
        'css_class': css_class,
    }

