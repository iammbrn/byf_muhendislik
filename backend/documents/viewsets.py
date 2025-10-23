from rest_framework import viewsets, permissions
from .models import Document
from .serializers import DocumentSerializer


class IsAdminOrFirmOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated and getattr(request.user, 'user_type', '') == 'admin':
            return True
        return getattr(request.user, 'firm', None) == obj.firm and obj.is_visible_to_firm

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class DocumentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [IsAdminOrFirmOwner]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, 'user_type', '') == 'admin':
            return Document.objects.all()
        return Document.objects.filter(firm=user.firm, is_visible_to_firm=True)

