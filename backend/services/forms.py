from django import forms
from .models import ServiceRequest

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['service_type', 'title', 'description', 'priority', 'requested_completion_date']
        widgets = {
            'service_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Talep başlığı'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Talep detayları'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'requested_completion_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {
            'service_type': 'Hizmet Türü',
            'title': 'Talep Başlığı',
            'description': 'Talep Açıklaması',
            'priority': 'Öncelik',
            'requested_completion_date': 'İstenen Tamamlanma Tarihi',
        }