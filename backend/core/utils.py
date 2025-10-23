import random
import string
from django.core.mail import send_mail
from django.conf import settings
from .models import ActivityLog

def generate_secure_password(length=12):
    """Güvenli şifre oluştur"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.SystemRandom().choice(characters) for _ in range(length))

def send_credentials_email(email, username, password, firm_name):
    """Kullanıcı bilgilerini e-posta ile gönder"""
    subject = f'BYF Mühendislik - {firm_name} Kullanıcı Bilgileriniz'
    message = f'''
Sayın {firm_name},
    
BYF Mühendislik sistemine erişim bilgileriniz aşağıda belirtilmiştir:
    
Sistem Adresi: {getattr(settings, 'SITE_URL', 'http://localhost:8000')}
Kullanıcı Adı: {username}
Şifre: {password}
    
Güvenliğiniz için ilk girişten sonra şifrenizi değiştirmenizi öneririz.
    
Saygılarımızla,
BYF Mühendislik
    '''
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )


def log_activity(user, action, message):
    """Log user activity - fails silently to not interrupt main flow"""
    try:
        ActivityLog.objects.create(user=user, action=action, message=message)
    except Exception:
        pass  # Activity logging is non-critical, don't interrupt main operations


# Common helper functions for views
def is_admin(user):
    """Check if user is admin"""
    return user.user_type == 'admin'


def is_firm(user):
    """Check if user is firm"""
    return user.user_type == 'firma'


def check_firm_access(user, firm_obj):
    """Check if firm user has access to specific firm object"""
    return hasattr(user, 'firm') and user.firm == firm_obj