"""Service-related utility functions for status resolution and common operations"""

from .models import Service, ServiceRequest


def resolve_service_request_status(service_request):
    """
    Get the real status of a ServiceRequest by checking its related Service.
    
    When a ServiceRequest is approved, an admin creates a Service to track the actual work.
    This function ensures we display the real work status (from Service) rather than
    the initial request status (from ServiceRequest).
    
    Args:
        service_request (ServiceRequest): The service request instance
        
    Returns:
        dict: {
            'related_service': Service instance or None,
            'display_status': str (status code like 'completed', 'in_progress'),
            'display_status_text': str (human-readable status like 'Tamamlandı')
        }
    
    Example:
        >>> sr = ServiceRequest.objects.get(id=1)
        >>> result = resolve_service_request_status(sr)
        >>> print(result['display_status_text'])
        'Tamamlandı'  # Shows Service status, not ServiceRequest status
    """
    related_service = None
    display_status = service_request.status
    display_status_text = service_request.get_status_display()
    
    # Only look for Service if the request has been processed
    if service_request.status in ['approved', 'in_progress', 'completed']:
        # Find the related Service by matching firm and title
        related_service = Service.objects.filter(
            firm=service_request.firm,
            name__icontains=service_request.title
        ).first()
        
        # If a Service exists, use its status (the real work status)
        if related_service:
            display_status = related_service.status
            display_status_text = related_service.get_status_display()
    
    return {
        'related_service': related_service,
        'display_status': display_status,
        'display_status_text': display_status_text,
    }


def enrich_service_requests_with_status(service_requests):
    """
    Enrich a queryset or list of ServiceRequests with real Service status information.
    
    This function processes multiple ServiceRequests and attaches the real Service
    status to each one, making it easy to display accurate status in templates.
    
    Args:
        service_requests: QuerySet or list of ServiceRequest instances
        
    Returns:
        list: List of dicts, each containing:
            - 'request': The ServiceRequest instance
            - 'related_service': Related Service instance or None
            - 'display_status': Status code to use
            - 'display_status_text': Human-readable status text
    
    Example:
        >>> requests = ServiceRequest.objects.filter(firm=my_firm)
        >>> enriched = enrich_service_requests_with_status(requests)
        >>> for item in enriched:
        ...     print(f"{item['request'].title}: {item['display_status_text']}")
        Test Service: Tamamlandı
    """
    enriched = []
    for sr in service_requests:
        status_info = resolve_service_request_status(sr)
        enriched.append({
            'request': sr,
            **status_info  # Unpack status_info dict
        })
    return enriched

