from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django import forms
from django_ratelimit.decorators import ratelimit

from .forms import CustomAuthenticationForm
from firms.models import Firm
from services.models import Service, ServiceRequest
from services.utils import enrich_service_requests_with_status
from documents.models import Document

# Reusable form for username changes
class UsernameForm(forms.Form):
    username = forms.CharField(max_length=150, label='Kullanıcı Adı')

def _get_dashboard_by_user_type(user_type):
    """Helper to get appropriate dashboard name"""
    return 'admin_dashboard' if user_type == 'admin' else 'firm_dashboard'

@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def custom_login(request):
    if request.user.is_authenticated:
        return redirect(_get_dashboard_by_user_type(request.user.user_type))
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None and user.is_active:
                login(request, user)
                # Remember-me: if not selected, session expires at browser close
                remember_me = request.POST.get('remember_me')
                request.session.set_expiry(60 * 60 * 24 * 14 if remember_me else 0)
                messages.success(request, 'Başarıyla giriş yaptınız.')
                return redirect(_get_dashboard_by_user_type(user.user_type))
            else:
                messages.error(request, 'Geçersiz kullanıcı adı veya şifre.')
        else:
            messages.error(request, 'Lütfen bilgilerinizi kontrol edin.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def custom_logout(request):
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('home')

@login_required
def admin_dashboard(request):
    if request.user.user_type != 'admin':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('firm_dashboard')
    
    from core.models import ContactMessage
    
    # Stat card verileri - 4 adet
    total_firms = Firm.objects.count()
    total_services = Service.objects.count()
    pending_requests = ServiceRequest.objects.filter(status='pending').count()
    pending_messages = ContactMessage.objects.filter(status='new').count()
    
    # Liste verileri
    recent_services = Service.objects.all().order_by('-request_date')[:5]
    recent_firms = Firm.objects.all().order_by('-registration_date')[:5]
    
    context = {
        'total_firms': total_firms,
        'total_services': total_services,
        'pending_requests': pending_requests,
        'pending_messages': pending_messages,
        'recent_services': recent_services,
        'recent_firms': recent_firms,
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@login_required
def firm_dashboard(request):
    if request.user.user_type != 'firma':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('admin_dashboard')
    
    try:
        firm = request.user.firm
        # Devam eden hizmetler - sadece son 1
        in_progress_services = firm.services.filter(status='in_progress').order_by('-request_date')[:1]
        in_progress_count = firm.services.filter(status='in_progress').count()
        
        # Tamamlanmış hizmetler - sadece son 1
        completed_services = firm.services.filter(status='completed').order_by('-completion_date')[:1]
        completed_count = firm.services.filter(status='completed').count()
        
        # Dokümanlar - sadece son 1
        documents = firm.documents.filter(is_visible_to_firm=True).order_by('-upload_date')[:1]
        documents_count = firm.documents.filter(is_visible_to_firm=True).count()
        
        # Sadece pending, approved ve in_progress durumundaki talepler - sadece son 1
        service_requests = firm.service_requests.filter(status__in=['pending', 'approved', 'in_progress']).order_by('-request_date')[:1]
        requests_count = firm.service_requests.filter(status__in=['pending', 'approved', 'in_progress']).count()
        
        # ServiceRequest'leri gerçek Service durumları ile zenginleştir
        requests_with_services = enrich_service_requests_with_status(service_requests)
        
        context = {
            'firm': firm,
            'recent_services': in_progress_services,
            'in_progress_count': in_progress_count,
            'completed_services': completed_services,
            'completed_count': completed_count,
            'recent_documents': documents,
            'documents_count': documents_count,
            'recent_requests': service_requests,
            'requests_with_services': requests_with_services,
            'requests_count': requests_count,
        }
        return render(request, 'accounts/firm_dashboard.html', context)
    except Firm.DoesNotExist:
        messages.error(request, 'Firma bilgileriniz bulunamadı.')
        return redirect('custom_logout')


def _handle_settings_view(request, user_type, template_name, settings_url_name):
    """Consolidated settings view for both admin and firm users"""
    # Access control
    if request.user.user_type != user_type:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        opposite_dashboard = 'firm_dashboard' if user_type == 'admin' else 'admin_dashboard'
        return redirect(opposite_dashboard)
    
    username_form = UsernameForm(initial={'username': request.user.username})
    password_form = PasswordChangeForm(user=request.user)
    
    if request.method == 'POST':
        if 'save_username' in request.POST:
            username_form = UsernameForm(request.POST)
            if username_form.is_valid():
                new_username = username_form.cleaned_data['username']
                User = get_user_model()
                if User.objects.filter(username=new_username).exclude(pk=request.user.pk).exists():
                    messages.error(request, 'Bu kullanıcı adı zaten kullanılıyor.')
                else:
                    request.user.username = new_username
                    request.user.save(update_fields=['username'])
                    messages.success(request, 'Kullanıcı adınız güncellendi.')
                    return redirect(settings_url_name)
        elif 'save_password' in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Şifreniz güncellendi.')
                return redirect(settings_url_name)
    
    return render(request, template_name, {
        'username_form': username_form,
        'password_form': password_form,
    })

@login_required
def admin_settings(request):
    return _handle_settings_view(request, 'admin', 'accounts/admin_settings.html', 'admin_settings')

@login_required
def firm_settings(request):
    return _handle_settings_view(request, 'firma', 'accounts/firm_settings.html', 'firm_settings')