from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Document


@receiver(post_save, sender=Document)
def notify_firm_on_document_upload(sender, instance: Document, created, **kwargs):
    if not created:
        return
    firm_email = instance.firm.email
    if not firm_email:
        return
    subject = f'Yeni Doküman Yüklendi: {instance.name}'
    message = (
        f"Sayın {instance.firm.name},\n\n"
        f"Hesabınıza yeni bir doküman yüklendi.\n"
        f"Doküman: {instance.name}\n"
        f"Tür: {instance.get_document_type_display()}\n\n"
        f"Sisteme giriş yaparak görüntüleyebilirsiniz.\n"
    )
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [firm_email], fail_silently=True)
    except Exception:
        pass


@receiver(post_save, sender=Document)
def complete_service_on_document_upload(sender, instance, created, **kwargs):
    """Auto-complete service when document is uploaded"""
    if created and instance.service and instance.service.status != 'completed':
        service = instance.service
        service.status = 'completed'
        if not service.completion_date:
            service.completion_date = timezone.now().date()
        service.save(update_fields=['status', 'completion_date'])
