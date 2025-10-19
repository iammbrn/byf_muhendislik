from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils.dateparse import parse_date

from .models import Service, ServiceRequest
from .forms import ServiceRequestForm
from .utils import enrich_service_requests_with_status
from core.utils import is_admin, is_firm, check_firm_access


def _validate_service_request_modification(request, service_request):
    """Helper: Validate if user can modify service request"""
    if request.method != 'POST':
        return {'success': False, 'error': 'Geçersiz istek'}
    
    if not is_firm(request.user):
        return {'success': False, 'error': 'Yetkiniz yok'}
    
    if not check_firm_access(request.user, service_request.firm):
        return {'success': False, 'error': 'Bu talebe erişim yetkiniz yok'}
    
    if service_request.status not in ['pending', 'approved']:
        return {'success': False, 'error': 'Bu talep değiştirilemez'}
    
    return None  # Validation passed

@login_required
def service_list(request):
    """Devam eden hizmetler listesi"""
    if request.user.user_type == 'admin':
        qs = Service.objects.all()
    else:
        qs = request.user.firm.services.all()

    # Sadece "Devam Ediyor" (in_progress) durumundaki hizmetleri göster
    qs = qs.filter(status='in_progress')

    # Filters
    service_type = request.GET.get('service_type')
    q = request.GET.get('q')
    if service_type:
        qs = qs.filter(service_type=service_type)
    if q:
        qs = qs.filter(name__icontains=q)

    services = qs.order_by('-request_date')

    context = {
        'services': services,
        'filters': {
            'service_type': service_type or '',
            'q': q or '',
        }
    }
    return render(request, 'services/service_list.html', context)


@login_required
def all_services(request):
    """Tüm hizmetler listesi - sadece admin için"""
    if not is_admin(request.user):
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('firm_dashboard')
    
    services = Service.objects.select_related('firm', 'assigned_admin').all()
    
    # Filtreler
    status_filter = request.GET.get('status')
    service_type = request.GET.get('service_type')
    search_query = request.GET.get('search')
    firm_id = request.GET.get('firm')
    
    if status_filter:
        services = services.filter(status=status_filter)
    
    if service_type:
        services = services.filter(service_type=service_type)
    
    if search_query:
        services = services.filter(name__icontains=search_query)
    
    if firm_id:
        services = services.filter(firm_id=firm_id)
    
    services = services.order_by('-request_date')
    
    # İstatistikler
    total_services = Service.objects.count()
    completed_count = Service.objects.filter(status='completed').count()
    in_progress_count = Service.objects.filter(status='in_progress').count()
    pending_count = Service.objects.filter(status='pending').count()
    cancelled_count = Service.objects.filter(status='cancelled').count()
    
    # Firma listesi (filtre için)
    from firms.models import Firm
    firms = Firm.objects.all().order_by('name')
    
    context = {
        'services': services,
        'total_services': total_services,
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'pending_count': pending_count,
        'cancelled_count': cancelled_count,
        'firms': firms,
        'filters': {
            'status': status_filter or '',
            'service_type': service_type or '',
            'search': search_query or '',
            'firm': firm_id or '',
        },
        'page_title': 'Tüm Hizmetler',
    }
    return render(request, 'services/all_services.html', context)

@login_required
def service_detail(request, service_id):
    service = get_object_or_404(Service.objects.select_related('firm', 'assigned_admin'), id=service_id)
    
    # Access control
    if not is_admin(request.user) and not check_firm_access(request.user, service.firm):
        messages.error(request, 'Bu hizmete erişim yetkiniz yok.')
        return redirect('service_list')
    
    # Admin sees all documents, firm only visible ones
    documents = service.documents.select_related('uploaded_by').all()
    if not is_admin(request.user):
        documents = documents.filter(is_visible_to_firm=True)
    documents = documents.order_by('-upload_date')
    
    context = {
        'service': service,
        'documents': documents,
    }
    return render(request, 'services/service_detail.html', context)

@login_required
def create_service_request(request):
    if not is_firm(request.user):
        messages.error(request, 'Sadece firmalar hizmet talebi oluşturabilir.')
        return redirect('firm_dashboard')
    
    if request.method == 'POST':
        form = ServiceRequestForm(request.POST)
        if form.is_valid():
            service_request = form.save(commit=False)
            service_request.firm = request.user.firm
            service_request.save()
            # Notify admin via email (basic)
            try:
                send_mail(
                    subject=f"Yeni Hizmet Talebi: {service_request.title} ({service_request.tracking_code})",
                    message=f"Firma: {service_request.firm.name}\nTür: {service_request.get_service_type_display()}\nTakip Kodu: {service_request.tracking_code}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.EMAIL_HOST_USER or settings.DEFAULT_FROM_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass
            messages.success(request, 'Hizmet talebiniz başarıyla oluşturuldu.')
            return redirect('firm_dashboard')
    else:
        form = ServiceRequestForm()
    
    return render(request, 'services/create_request.html', {'form': form})


@login_required
def service_request_detail(request, request_id):
    service_request = get_object_or_404(ServiceRequest.objects.select_related('firm', 'responded_by'), id=request_id)
    
    # Access control - only related firm or admin can view
    if is_firm(request.user) and not check_firm_access(request.user, service_request.firm):
        messages.error(request, 'Bu talebe erişim yetkiniz yok.')
        return redirect('firm_dashboard')
    
    # İlgili Service'i bul
    related_service = None
    documents = []
    
    if service_request.status in ['approved', 'in_progress', 'completed']:
        # Bu talebe karşılık gelen Service'i bul
        related_service = Service.objects.filter(
            firm=service_request.firm,
            name__icontains=service_request.title
        ).first()
        
        if related_service:
            # Service'e ait firmaya görünür dokümanları getir
            documents = related_service.documents.filter(is_visible_to_firm=True).order_by('-upload_date')
    
    context = {
        'service_request': service_request,
        'related_service': related_service,
        'documents': documents,
    }
    return render(request, 'services/service_request_detail.html', context)


@login_required
def cancel_service_request(request, request_id):
    """Firma kullanıcısının hizmet talebini iptal etmesi"""
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    # Validate permissions
    error = _validate_service_request_modification(request, service_request)
    if error:
        return JsonResponse(error)
    
    service_request.status = 'rejected'
    service_request.save()
    
    return JsonResponse({'success': True, 'message': 'Talep iptal edildi'})


@login_required
def delete_service_request(request, request_id):
    """Firma kullanıcısının hizmet talebini silmesi"""
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    # Validate permissions
    error = _validate_service_request_modification(request, service_request)
    if error:
        return JsonResponse(error)
    
    service_request.delete()
    
    return JsonResponse({'success': True, 'message': 'Talep silindi'})


@login_required
def completed_services(request):
    """Tamamlanan hizmetler listesi - hem firma hem admin için"""
    if is_admin(request.user):
        services = Service.objects.select_related('firm', 'assigned_admin').filter(status='completed')
    else:
        if not hasattr(request.user, 'firm'):
            messages.error(request, 'Firma bilgileriniz bulunamadı.')
            return redirect('custom_logout')
        services = request.user.firm.services.select_related('assigned_admin').filter(status='completed')
    
    # Filtreler
    service_type = request.GET.get('service_type')
    search_query = request.GET.get('search')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if service_type:
        services = services.filter(service_type=service_type)
    
    if search_query:
        services = services.filter(name__icontains=search_query)
    
    if start_date:
        services = services.filter(completion_date__gte=start_date)
    
    if end_date:
        services = services.filter(completion_date__lte=end_date)
    
    services = services.order_by('-completion_date')
    
    context = {
        'services': services,
        'page_title': 'Tamamlanan Hizmetler',
        'filters': {
            'service_type': service_type or '',
            'search': search_query or '',
            'start_date': start_date or '',
            'end_date': end_date or '',
        }
    }
    return render(request, 'services/completed_services.html', context)


@login_required
def service_request_list(request):
    """Firma kullanıcısı için hizmet talepleri listesi"""
    if not is_firm(request.user):
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('admin_dashboard')
    
    if not hasattr(request.user, 'firm'):
        messages.error(request, 'Firma bilgileriniz bulunamadı.')
        return redirect('custom_logout')
    
    # Firmaya ait tüm hizmet taleplerini al
    service_requests = request.user.firm.service_requests.all().order_by('-request_date')
    
    # Filtreler
    status_filter = request.GET.get('status')
    if status_filter:
        service_requests = service_requests.filter(status=status_filter)
    
    # ServiceRequest'leri gerçek Service durumları ile zenginleştir
    requests_with_services = enrich_service_requests_with_status(service_requests)
    
    context = {
        'service_requests': service_requests,
        'requests_with_services': requests_with_services,
        'status_filter': status_filter or '',
        'page_title': 'Hizmet Taleplerim',
    }
    return render(request, 'services/service_request_list.html', context)


@login_required
def update_service(request, service_id):
    """AJAX endpoint for updating service details"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Geçersiz istek'})
    
    if not is_admin(request.user):
        return JsonResponse({'success': False, 'error': 'Yetkiniz yok'})
    
    service = get_object_or_404(Service, id=service_id)
    
    try:
        # Get form data
        service.name = request.POST.get('name', service.name)
        service.service_type = request.POST.get('service_type', service.service_type)
        service.description = request.POST.get('description', service.description)
        service.status = request.POST.get('status', service.status)
        service.notes = request.POST.get('notes', service.notes)
        
        # Handle dates
        start_date = request.POST.get('start_date')
        if start_date:
            service.start_date = parse_date(start_date)
        
        completion_date = request.POST.get('completion_date')
        if completion_date:
            service.completion_date = parse_date(completion_date)
        
        service.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Hizmet başarıyla güncellendi',
            'service': {
                'name': service.name,
                'status': service.status,
                'status_display': service.get_status_display(),
            }
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})