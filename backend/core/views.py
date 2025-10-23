from django.shortcuts import render

def custom_403(request, exception):
    """Custom 403 Forbidden error page"""
    return render(request, '403.html', {'exception': exception}, status=403)

def custom_404(request, exception):
    """Custom 404 Not Found error page"""
    return render(request, '404.html', status=404)

def custom_500(request):
    """Custom 500 Server Error page"""
    return render(request, '500.html', status=500)