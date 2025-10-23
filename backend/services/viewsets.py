from rest_framework import viewsets, permissions
from .models import Service, ServiceRequest
from .serializers import ServiceSerializer, ServiceRequestSerializer


class IsAdminOrFirmOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and getattr(request.user, 'user_type', '') == 'admin':
            return True
        if hasattr(obj, 'firm'):
            return getattr(request.user, 'firm', None) == obj.firm
        return False

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class ServiceViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrFirmOwner]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'user_type', '') == 'admin':
            return Service.objects.all()
        return Service.objects.filter(firm=user.firm)


class ServiceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceRequestSerializer
    permission_classes = [IsAdminOrFirmOwner]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'user_type', '') == 'admin':
            return ServiceRequest.objects.all()
        return ServiceRequest.objects.filter(firm=user.firm)

    def perform_create(self, serializer):
        serializer.save(firm=self.request.user.firm)

