from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    phase_display = serializers.CharField(source='get_current_phase_display', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 
            'name', 
            'description', 
            'status', 
            'status_display',
            'current_phase', 
            'phase_display',
            'requirements_data',
            'blueprint_data',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

# Add to projects/serializers.py

class AnswerInputSerializer(serializers.Serializer):
    stage = serializers.ChoiceField(choices=[
        ('intent', 'App Intent'),
        ('platform', 'Platform & Devices'),
        ('ui_ux', 'UI / UX'),
        ('tech_stack', 'Tech Stack'),
        ('quality', 'Quality & Delivery')
    ])
    answer_data = serializers.JSONField()