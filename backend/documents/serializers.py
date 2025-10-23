from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)

    class Meta:
        model = Document
        fields = ['id', 'name', 'document_type', 'document_type_display', 'description', 'upload_date', 'service', 'file']

