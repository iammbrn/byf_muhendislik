from django.urls import path
from . import views
from rest_framework import routers
from .viewsets import DocumentViewSet

router = routers.DefaultRouter()
router.register(r'api/documents', DocumentViewSet, basename='api-documents')

urlpatterns = [
    path('', views.document_list, name='document_list'),
    path('<int:document_id>/', views.document_detail, name='document_detail'),
    path('<int:document_id>/indir/', views.download_document, name='download_document'),
    path('<int:document_id>/sil/', views.delete_document, name='delete_document'),
] + router.urls