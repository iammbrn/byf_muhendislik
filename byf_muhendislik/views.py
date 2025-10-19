from django.shortcuts import render
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django_ratelimit.decorators import ratelimit

from blog.models import BlogPost
from core.models import ContactMessage, ServiceCategory, TeamMember

def home(request):
    recent_posts = BlogPost.objects.filter(status='published').select_related('author')[:3]
    service_categories = ServiceCategory.objects.filter(is_active=True).order_by('order', 'title')
    
    return render(request, 'home.html', {
        'recent_posts': recent_posts,
        'service_categories': service_categories,
    })

def about(request):
    team_members = TeamMember.objects.filter(is_active=True).order_by('order', 'name')
    return render(request, 'about.html', {'team_members': team_members})

def services_list(request):
    """Hizmetlerimiz sayfası - dinamik"""
    service_categories = ServiceCategory.objects.filter(is_active=True).order_by('order', 'title')
    return render(request, 'services.html', {'service_categories': service_categories})

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        surname = request.POST.get('surname', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if not all([name, surname, phone, email, subject, message]):
            messages.error(request, 'Lütfen tüm zorunlu alanları doldurun.')
            return render(request, 'contact.html')

        try:
            # Veritabanına kaydet
            contact_msg = ContactMessage.objects.create(
                name=name,
                surname=surname,
                phone=phone,
                email=email,
                subject=subject,
                message=message,
                status='new'
            )

            # E-posta gönder
            full_subject = f"İletişim Formu: {subject} - {name} {surname}"
            full_message = (
                f"Ad Soyad: {name} {surname}\n"
                f"Telefon: {phone}\n"
                f"E-posta: {email}\n"
                f"Konu: {subject}\n\n"
                f"Mesaj:\n{message}"
            )

            send_mail(
                full_subject,
                full_message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
            
            messages.success(request, 'Mesajınız başarıyla gönderildi! En kısa sürede size geri dönüş yapacağız.')
        except Exception as e:
            messages.error(request, 'Mesaj gönderilirken bir hata oluştu. Lütfen daha sonra tekrar deneyin.')
            
    return render(request, 'contact.html')