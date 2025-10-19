from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import CustomPasswordResetForm

urlpatterns = [
    path('giris/', views.custom_login, name='custom_login'),
    path('cikis/', views.custom_logout, name='custom_logout'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('firma-paneli/', views.firm_dashboard, name='firm_dashboard'),
    path('ayarlar/', views.admin_settings, name='admin_settings'),
    path('firma-ayarlari/', views.firm_settings, name='firm_settings'),
    # Password reset
    path('sifre-sifirla/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        form_class=CustomPasswordResetForm,
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt'
    ), name='password_reset'),
    path('sifre-sifirla/dogrulama/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('sifre-sifirla/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html'), name='password_reset_confirm'),
    path('sifre-sifirla/tamam/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
]