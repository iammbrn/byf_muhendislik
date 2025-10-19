from django.urls import path
from . import views
from rest_framework import routers
from .viewsets import ServiceViewSet, ServiceRequestViewSet

router = routers.DefaultRouter()
router.register(r'api/services', ServiceViewSet, basename='api-services')
router.register(r'api/requests', ServiceRequestViewSet, basename='api-requests')

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('tum-hizmetler/', views.all_services, name='all_services'),
    path('tamamlanan/', views.completed_services, name='completed_services'),
    path('taleplerim/', views.service_request_list, name='service_request_list'),
    path('<int:service_id>/', views.service_detail, name='service_detail'),
    path('<int:service_id>/guncelle/', views.update_service, name='update_service'),
    path('talep-olustur/', views.create_service_request, name='create_service_request'),
    path('talep/<int:request_id>/', views.service_request_detail, name='service_request_detail'),
    path('talep/<int:request_id>/iptal/', views.cancel_service_request, name='cancel_service_request'),
    path('talep/<int:request_id>/sil/', views.delete_service_request, name='delete_service_request'),
] + router.urls