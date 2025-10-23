from django.shortcuts import redirect
from django.contrib import messages

class UserTypeMiddleware:
    """Redirects users to appropriate dashboard based on user_type"""
    
    ROUTE_MAPPINGS = {
        '/hesap/dashboard/': ('admin', 'firm_dashboard'),
        '/hesap/firma-paneli/': ('firma', 'admin_dashboard'),
    }
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return None
            
        for path, (required_type, redirect_to) in self.ROUTE_MAPPINGS.items():
            if request.path.startswith(path) and request.user.user_type != required_type:
                messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
                return redirect(redirect_to)
        
        return None