from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django import forms

from .models import Firm
from core.utils import is_admin


@login_required
def firm_list(request):
    if not is_admin(request.user):
        return redirect('firm_dashboard')
    
    firms = Firm.objects.all().order_by('-registration_date')
    return render(request, 'firms/firm_list.html', {'firms': firms})

@login_required
def firm_detail(request, firm_id):
    if not is_admin(request.user):
        return redirect('firm_dashboard')
    
    firm = get_object_or_404(Firm, id=firm_id)
    services = firm.services.select_related('firm').all().order_by('-request_date')
    documents = firm.documents.select_related('service').all().order_by('-upload_date')
    
    return render(request, 'firms/firm_detail.html', {
        'firm': firm,
        'services': services,
        'documents': documents,
    })


# Firm profile update form
class FirmProfileForm(forms.ModelForm):
    class Meta:
        model = Firm
        fields = ['phone', 'email', 'address', 'contact_person', 'contact_person_title', 'website', 'city']


@login_required
def firm_profile(request):
    if request.user.user_type != 'firma':
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('admin_dashboard')

    firm = request.user.firm
    if request.method == 'POST':
        form = FirmProfileForm(request.POST, instance=firm)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profiliniz güncellendi.')
            return redirect('firm_profile')
    else:
        form = FirmProfileForm(instance=firm)

    return render(request, 'firms/firm_profile.html', {'form': form})