from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.contrib.auth import get_user_model
from captcha.fields import CaptchaField

User = get_user_model()

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='Kullanıcı Adı veya E-posta',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kullanıcı adı veya e-posta'})
    )
    password = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Şifre'})
    )
    captcha = CaptchaField()

class CustomPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        label='E-posta Adresi',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'E-posta adresinizi girin'}),
        error_messages={'required': 'E-posta adresi gereklidir.'}
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Email widget already validates format, but double-check just in case
        if email and '@' not in email:
            raise forms.ValidationError('Geçerli bir e-posta adresi girin.')
        # Note: Not checking if user exists for security (prevents email enumeration)
        return email