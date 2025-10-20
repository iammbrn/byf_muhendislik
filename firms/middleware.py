"""
Middleware to check firm status on each request.
Logs out users whose firms have been deactivated.
"""
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse


class FirmStatusMiddleware:
    """
    Middleware to check if a logged-in firm user's firm is still active.
    If the firm is inactive or suspended, log out the user.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check before processing the request
        if request.user.is_authenticated and request.user.user_type == 'firma':
            # Skip check for logout and login pages to avoid redirect loops
            current_path = request.path
            if current_path not in [reverse('custom_logout'), reverse('custom_login')]:
                try:
                    firm = request.user.firm
                    if firm.status != 'active':
                        # Log out the user
                        logout(request)
                        messages.warning(request, 'Hesabınız pasif duruma alındı. Giriş yapamazsınız.')
                        
                        # Redirect to login page
                        return redirect('custom_login')
                except Exception:
                    # If firm doesn't exist or any error, log out for safety
                    logout(request)
                    messages.error(request, 'Firma bilgileriniz bulunamadı.')
                    return redirect('custom_login')
        
        response = self.get_response(request)
        return response

