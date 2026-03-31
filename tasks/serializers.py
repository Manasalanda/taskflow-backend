from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    is_overdue = serializers.ReadOnlyField()
    project_title = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id', 'project', 'project_title', 'title', 'description',
            'priority', 'status', 'deadline', 'estimated_hours',
            'scheduled_date', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_project_title(self, obj):
        return obj.project.title if obj.project else None

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)