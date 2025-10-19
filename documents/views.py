from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404, FileResponse
from django.contrib import messages
from django.db.models import F
from urllib.parse import quote
import mimetypes
import os

from .models import Document


def _check_document_access(user, document):
    """Helper: Check if user has access to document"""
    if user.user_type == 'admin':
        return True
    return hasattr(user, 'firm') and document.firm == user.firm and document.is_visible_to_firm


@login_required
def document_list(request):
    if request.user.user_type == 'admin':
        documents = Document.objects.select_related('firm', 'service').all().order_by('-upload_date')
    else:
        if not hasattr(request.user, 'firm'):
            messages.error(request, 'Firma bilgileriniz bulunamadı.')
            return redirect('custom_logout')
        documents = request.user.firm.documents.select_related('service').filter(is_visible_to_firm=True).order_by('-upload_date')
    
    # Filter by service if provided
    service_id = request.GET.get('service')
    if service_id:
        documents = documents.filter(service_id=service_id)
    
    return render(request, 'documents/document_list.html', {'documents': documents})

@login_required
def document_detail(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    if not _check_document_access(request.user, document):
        raise Http404("Doküman bulunamadı.")
    
    # Atomic view count increment
    Document.objects.filter(id=document.id).update(download_count=F('download_count') + 1)
    
    return render(request, 'documents/document_detail.html', {'document': document})

@login_required
def download_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    
    if not _check_document_access(request.user, document):
        raise Http404("Doküman bulunamadı.")
    
    # Atomic download count increment
    Document.objects.filter(id=document.id).update(download_count=F('download_count') + 1)
    
    # Download file
    try:
        original_filename = os.path.basename(document.file.name)
        response = FileResponse(document.file.open('rb'), as_attachment=True)
        
        # Set filename with UTF-8 encoding support
        encoded_filename = quote(original_filename)
        response['Content-Disposition'] = f'attachment; filename="{original_filename}"; filename*=UTF-8\'\'{encoded_filename}'
        
        # Set MIME type
        content_type = mimetypes.guess_type(original_filename)[0] or 'application/octet-stream'
        response['Content-Type'] = content_type
        
        return response
    except Exception:
        messages.error(request, 'Dosya indirilemedi.')
        return redirect('document_list')

@login_required
def delete_document(request, document_id):
    """Firma kullanıcılarının ve admin'in doküman silmesi"""
    document = get_object_or_404(Document, id=document_id)
    
    # Erişim kontrolü - admin veya firma sahibi silebilir
    can_delete = False
    if request.user.user_type == 'admin':
        can_delete = True
    elif request.user.user_type == 'firma':
        if hasattr(request.user, 'firm') and document.firm == request.user.firm:
            can_delete = True
    
    if can_delete:
        service_id = document.service_id if document.service else None
        document.delete()
        messages.success(request, 'Doküman başarıyla silindi.')
        
        # Eğer service'den geliyorsak oraya yönlendir
        if service_id and request.GET.get('from') == 'service':
            return redirect('service_detail', service_id=service_id)
    else:
        messages.error(request, 'Bu dokümanı silme yetkiniz yok.')
    
    return redirect('document_list')