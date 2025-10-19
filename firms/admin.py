from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Firm, FirmServiceHistory
from core.utils import generate_secure_password, log_activity
from core.models import ProvisionedCredential


def generate_username_from_firm_name(firm_name):
    """Generate unique username from firm name"""
    User = get_user_model()
    base = firm_name.lower().replace(' ', '_')
    base = ''.join(ch for ch in base if ch.isalnum() or ch == '_') or 'firma'
    
    username = base
    suffix = 0
    while User.objects.filter(username=username).exists():
        suffix += 1
        username = f"{base}{suffix}"
    
    return username


@admin.register(Firm)
class FirmAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'phone', 'email', 'city', 'status', 'registration_date')
    list_filter = ('status', 'city', 'registration_date')
    search_fields = ('name', 'contact_person', 'email', 'tax_number')
    readonly_fields = ('registration_date', 'updated_at', 'unique_id')

    def save_model(self, request, obj, form, change):
        is_new = obj.pk is None
        super().save_model(request, obj, form, change)
        
        if is_new:
            User = get_user_model()
            username = generate_username_from_firm_name(obj.name)
            password = generate_secure_password(length=14)
            
            user = User.objects.create_user(
                username=username,
                email=obj.email,
                password=password,
                user_type='firma'
            )
            
            ProvisionedCredential.objects.create(
                user=user,
                username=username,
                password_plain=password,
                is_admin=False,
            )
            
            obj.user = user
            obj.save(update_fields=['user'])
            log_activity(request.user, 'create', f'Firma için kullanıcı oluşturuldu: {obj.name} -> {username}')

@admin.register(FirmServiceHistory)
class FirmServiceHistoryAdmin(admin.ModelAdmin):
    list_display = ('firm', 'service_type', 'service_date', 'completion_date')
    list_filter = ('service_type', 'service_date')
    search_fields = ('firm__name', 'service_type')