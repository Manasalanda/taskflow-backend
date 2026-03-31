from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    total_tasks = serializers.ReadOnlyField()
    completed_tasks = serializers.ReadOnlyField()
    progress_percentage = serializers.ReadOnlyField()

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'description', 'start_date', 'end_date',
            'total_tasks', 'completed_tasks', 'progress_percentage',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)