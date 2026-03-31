from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from tasks.models import Task
from projects.models import Project
from tasks.serializers import TaskSerializer
from .groq_service import generate_schedule, reschedule_tasks, get_task_priority_suggestions
import logging

logger = logging.getLogger(__name__)

class GenerateScheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        project_id = request.data.get('project_id')
        user = request.user

        try:
            if project_id:
                project = Project.objects.get(id=project_id, user=user)
                tasks = Task.objects.filter(project=project, status__in=['pending', 'in_progress'])
                project_info = {
                    'title': project.title,
                    'end_date': str(project.end_date)
                }
            else:
                tasks = Task.objects.filter(user=user, status__in=['pending', 'in_progress'])
                project_info = {'title': 'All Tasks', 'end_date': None}

            tasks_data = TaskSerializer(tasks, many=True).data

            if not tasks_data:
                return Response({'error': 'No active tasks found to schedule.'}, status=400)

            user_settings = {
                'work_hours_per_day': user.work_hours_per_day,
                'preferred_working_time': user.preferred_working_time,
                'max_tasks_per_day': user.max_tasks_per_day,
                'break_interval_minutes': user.break_interval_minutes,
            }

            schedule = generate_schedule(list(tasks_data), user_settings, project_info)
            return Response({'schedule': schedule, 'task_count': len(tasks_data)})

        except Project.DoesNotExist:
            return Response({'error': 'Project not found.'}, status=404)
        except Exception as e:
            logger.error(f"Schedule generation error: {str(e)}")
            return Response({'error': f'AI service error: {str(e)}'}, status=500)


class RescheduleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        missed_days = request.data.get('missed_days', 1)
        project_id = request.data.get('project_id')
        user = request.user

        try:
            if project_id:
                tasks = Task.objects.filter(
                    project_id=project_id,
                    user=user,
                    status__in=['pending', 'in_progress']
                )
            else:
                tasks = Task.objects.filter(user=user, status__in=['pending', 'in_progress'])

            tasks_data = TaskSerializer(tasks, many=True).data

            if not tasks_data:
                return Response({'error': 'No tasks to reschedule.'}, status=400)

            user_settings = {
                'work_hours_per_day': user.work_hours_per_day,
                'max_tasks_per_day': user.max_tasks_per_day,
            }

            result = reschedule_tasks(missed_days, list(tasks_data), user_settings)
            return Response({'rescheduled': result, 'missed_days': missed_days})

        except Exception as e:
            logger.error(f"Reschedule error: {str(e)}")
            return Response({'error': f'AI service error: {str(e)}'}, status=500)


class PrioritySuggestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tasks = Task.objects.filter(
            user=request.user,
            status__in=['pending', 'in_progress']
        )
        tasks_data = [
            {
                'id': t.id,
                'title': t.title,
                'priority': t.priority,
                'deadline': str(t.deadline) if t.deadline else None
            }
            for t in tasks
        ]

        if not tasks_data:
            return Response({'error': 'No tasks to analyze.'}, status=400)

        try:
            suggestions = get_task_priority_suggestions(tasks_data)
            return Response(suggestions)
        except Exception as e:
            return Response({'error': str(e)}, status=500)