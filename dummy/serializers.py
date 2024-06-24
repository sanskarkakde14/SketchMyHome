from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['project_name', 'width', 'length', 'bedroom', 'bathroom', 'car', 'temple', 'garden', 'living_room', 'store_room']
        
class PDFSerializer(serializers.Serializer):
    name = serializers.CharField()
    url = serializers.URLField()