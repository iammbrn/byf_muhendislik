from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import os
import uuid

def document_upload_path(instance, filename):
    if instance.firm:
        return f'documents/firm_{instance.firm.id}/{instance.document_type}/{filename}'
    return f'documents/general/{instance.document_type}/{filename}'

class Document(models.Model):
    DOCUMENT_TYPES = (
        ('service_report', 'Hizmet Raporu'),
        ('certificate', 'Sertifika'),
        ('invoice', 'Fatura'),
        ('contract', 'Sözleşme'),
        ('technical_drawing', 'Teknik Çizim'),
        ('other', 'Diğer'),
    )
    
    name = models.CharField(max_length=255, verbose_name='Dosya Adı')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES, verbose_name='Dosya Türü')
    file = models.FileField(upload_to=document_upload_path, verbose_name='Dosya')
    firm = models.ForeignKey('firms.Firm', on_delete=models.CASCADE, related_name='documents')
    service = models.ForeignKey('services.Service', on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='uploaded_documents')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    upload_date = models.DateTimeField(auto_now_add=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_visible_to_firm = models.BooleanField(default=True, verbose_name='Firmaya Görünür')
    version = models.PositiveIntegerField(default=1, verbose_name='Versiyon')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='versions', verbose_name='Önceki Versiyon')
    download_count = models.PositiveIntegerField(default=0, verbose_name='İndirme Sayısı')
    
    class Meta:
        verbose_name = 'Doküman'
        verbose_name_plural = 'Dokümanlar'
        ordering = ['-upload_date']
        indexes = [
            models.Index(fields=['-upload_date'], name='doc_upload_date_idx'),
            models.Index(fields=['firm', '-upload_date'], name='doc_firm_date_idx'),
            models.Index(fields=['service', '-upload_date'], name='doc_service_date_idx'),
            models.Index(fields=['document_type', '-upload_date'], name='doc_type_date_idx'),
            models.Index(fields=['is_visible_to_firm', '-upload_date'], name='doc_visible_date_idx'),
        ]
        db_table_comment = 'Doküman yönetimi - firmalar için dosya saklama'
    
    def __str__(self):
        return self.name
    
    def filename(self):
        return os.path.basename(self.file.name)
    
    def file_extension(self):
        name, extension = os.path.splitext(self.file.name)
        return extension.lower()

    def clean(self):
        super().clean()
        # Basic file validation
        max_size = 50 * 1024 * 1024  # 50MB
        allowed_extensions = {
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.png', '.jpg', '.jpeg'
        }
        if self.file:
            ext = self.file_extension()
            if ext not in allowed_extensions:
                raise ValidationError({'file': 'İzin verilmeyen dosya türü.'})
            if hasattr(self.file, 'size') and self.file.size > max_size:
                raise ValidationError({'file': 'Dosya boyutu en fazla 50MB olmalıdır.'})