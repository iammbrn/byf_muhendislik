from rest_framework import serializers
from .models import Service, ServiceRequest


class ServiceSerializer(serializers.ModelSerializer):
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'service_type', 'service_type_display', 'description', 'status', 'status_display', 'request_date', 'start_date', 'completion_date', 'notes']


class ServiceRequestSerializer(serializers.ModelSerializer):
    service_type_display = serializers.CharField(source='get_service_type_display', read_only=True)

    class Meta:
        model = ServiceRequest
        fields = ['id', 'service_type', 'service_type_display', 'title', 'description', 'priority', 'status', 'request_date', 'updated_at', 'tracking_code']

