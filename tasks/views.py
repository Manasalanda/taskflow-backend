# from rest_framework import viewsets, status
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated
# from django.utils import timezone
# from django.db.models import Count, Q
# from .models import Task
# from .serializers import TaskSerializer

# class TaskViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = TaskSerializer

#     def get_queryset(self):
#         qs = Task.objects.filter(user=self.request.user)
#         project_id = self.request.query_params.get('project')
#         status_filter = self.request.query_params.get('status')
#         priority = self.request.query_params.get('priority')

#         if project_id:
#             qs = qs.filter(project_id=project_id)
#         if status_filter:
#             qs = qs.filter(status=status_filter)
#         if priority:
#             qs = qs.filter(priority=priority)
#         return qs

#     @action(detail=False, methods=['get'])
#     def dashboard_stats(self, request):
#         user = request.user
#         tasks = Task.objects.filter(user=user)
#         today = timezone.now().date()

#         stats = {
#             'total': tasks.count(),
#             'pending': tasks.filter(status='pending').count(),
#             'in_progress': tasks.filter(status='in_progress').count(),
#             'completed': tasks.filter(status='completed').count(),
#             'overdue': tasks.filter(deadline__lt=timezone.now(), status__in=['pending', 'in_progress']).count(),
#             'due_today': tasks.filter(deadline__date=today, status__in=['pending', 'in_progress']).count(),
#             'high_priority': tasks.filter(priority__in=['high', 'critical'], status__in=['pending', 'in_progress']).count(),
#         }

        

#         @action(detail=False, methods=['get'])
#         def alerts(self, request):
#          from django.utils import timezone
#         from datetime import timedelta

#     user = request.user
#     now = timezone.now()
#     tomorrow = now + timedelta(hours=24)

#     alerts = []

#     # Tasks due within 24 hours
#     due_soon = Task.objects.filter(
#         user=user,
#         status__in=['pending', 'in_progress'],
#         deadline__gte=now,
#         deadline__lte=tomorrow,
#     )
#     for task in due_soon:
#         hours_left = (task.deadline - now).seconds // 3600
#         total_seconds = (task.deadline - now).total_seconds()
#         hours_left = max(0, int(total_seconds // 3600))
#         minutes_left = max(0, int((total_seconds % 3600) // 60))

#         if hours_left == 0:
#             time_str = f"{minutes_left} minutes"
#         elif hours_left < 2:
#             time_str = f"{hours_left}h {minutes_left}m"
#         else:
#             time_str = f"{hours_left} hours"

#         alerts.append({
#             'id': f'due-{task.id}',
#             'type': 'warning',
#             'priority': task.priority,
#             'title': f'Deadline approaching: {task.title}',
#             'message': f'Due in {time_str}',
#             'task_id': task.id,
#         })

#     # Overdue tasks
#     overdue = Task.objects.filter(
#         user=user,
#         status__in=['pending', 'in_progress'],
#         deadline__lt=now,
#     )
#     for task in overdue:
#         days_overdue = (now - task.deadline).days
#         hours_overdue = int((now - task.deadline).total_seconds() // 3600)

#         if days_overdue == 0:
#             time_str = f"{hours_overdue} hours ago"
#         elif days_overdue == 1:
#             time_str = "yesterday"
#         else:
#             time_str = f"{days_overdue} days ago"

#         alerts.append({
#             'id': f'overdue-{task.id}',
#             'type': 'error',
#             'priority': task.priority,
#             'title': f'Overdue: {task.title}',
#             'message': f'Was due {time_str}',
#             'task_id': task.id,
#         })

#     # High priority pending tasks (no deadline)
#     high_priority = Task.objects.filter(
#         user=user,
#         status='pending',
#         priority__in=['high', 'critical'],
#         deadline__isnull=True,
#     )
#     for task in high_priority:
#         alerts.append({
#             'id': f'high-{task.id}',
#             'type': 'info',
#             'priority': task.priority,
#             'title': f'{task.priority.capitalize()} priority task pending',
#             'message': task.title,
#             'task_id': task.id,
#         })

#     # Sort: error first, then warning, then info
#     type_order = {'error': 0, 'warning': 1, 'info': 2}
#     alerts.sort(key=lambda x: type_order.get(x['type'], 3))
#     return Response({
#         'alerts': alerts,
#         'count': len(alerts),
#     })


#         # Productivity score: completed / total * 100
#     stats['productivity_score'] = round(
#      (stats['completed'] / stats['total'] * 100) if stats['total'] > 0 else 0, 1
#         )

#         # Monthly breakdown (last 6 months)
#     monthly = []
#     for i in range(5, -1, -1):
#             from dateutil.relativedelta import relativedelta
#             month_date = today - relativedelta(months=i)
#             completed = tasks.filter(
#                 status='completed',
#                 updated_at__year=month_date.year,
#                 updated_at__month=month_date.month
#             ).count()
#             monthly.append({
#                 'month': month_date.strftime('%b %Y'),
#                 'completed': completed
#             })
#             stats['monthly_breakdown'] = monthly
#             return Response(stats)


from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from .models import Task
from .serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        qs = Task.objects.filter(user=self.request.user)
        project_id = self.request.query_params.get('project')
        status_filter = self.request.query_params.get('status')
        priority = self.request.query_params.get('priority')
        if project_id:
            qs = qs.filter(project_id=project_id)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if priority:
            qs = qs.filter(priority=priority)
        return qs

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        from dateutil.relativedelta import relativedelta
        user = request.user
        tasks = Task.objects.filter(user=user)
        today = timezone.now().date()

        stats = {
            'total': tasks.count(),
            'pending': tasks.filter(status='pending').count(),
            'in_progress': tasks.filter(status='in_progress').count(),
            'completed': tasks.filter(status='completed').count(),
            'overdue': tasks.filter(
                deadline__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            ).count(),
            'due_today': tasks.filter(
                deadline__date=today,
                status__in=['pending', 'in_progress']
            ).count(),
            'high_priority': tasks.filter(
                priority__in=['high', 'critical'],
                status__in=['pending', 'in_progress']
            ).count(),
        }

        stats['productivity_score'] = round(
            (stats['completed'] / stats['total'] * 100)
            if stats['total'] > 0 else 0, 1
        )

        monthly = []
        for i in range(5, -1, -1):
            month_date = today - relativedelta(months=i)
            completed = tasks.filter(
                status='completed',
                updated_at__year=month_date.year,
                updated_at__month=month_date.month
            ).count()
            monthly.append({
                'month': month_date.strftime('%b %Y'),
                'completed': completed
            })
        stats['monthly_breakdown'] = monthly

        return Response(stats)

    @action(detail=False, methods=['get'])
    def alerts(self, request):
        user = request.user
        now = timezone.now()
        tomorrow = now + timedelta(hours=24)
        alerts = []

        due_soon = Task.objects.filter(
            user=user,
            status__in=['pending', 'in_progress'],
            deadline__gte=now,
            deadline__lte=tomorrow,
        )
        for task in due_soon:
            total_seconds = (task.deadline - now).total_seconds()
            hours_left = max(0, int(total_seconds // 3600))
            minutes_left = max(0, int((total_seconds % 3600) // 60))
            if hours_left == 0:
                time_str = f"{minutes_left} minutes"
            elif hours_left < 2:
                time_str = f"{hours_left}h {minutes_left}m"
            else:
                time_str = f"{hours_left} hours"
            alerts.append({
                'id': f'due-{task.id}',
                'type': 'warning',
                'priority': task.priority,
                'title': f'Deadline approaching: {task.title}',
                'message': f'Due in {time_str}',
                'task_id': task.id,
            })

        overdue = Task.objects.filter(
            user=user,
            status__in=['pending', 'in_progress'],
            deadline__lt=now,
        )
        for task in overdue:
            days_overdue = (now - task.deadline).days
            hours_overdue = int((now - task.deadline).total_seconds() // 3600)
            if days_overdue == 0:
                time_str = f"{hours_overdue} hours ago"
            elif days_overdue == 1:
                time_str = "yesterday"
            else:
                time_str = f"{days_overdue} days ago"
            alerts.append({
                'id': f'overdue-{task.id}',
                'type': 'error',
                'priority': task.priority,
                'title': f'Overdue: {task.title}',
                'message': f'Was due {time_str}',
                'task_id': task.id,
            })

        high_priority = Task.objects.filter(
            user=user,
            status='pending',
            priority__in=['high', 'critical'],
            deadline__isnull=True,
        )
        for task in high_priority:
            alerts.append({
                'id': f'high-{task.id}',
                'type': 'info',
                'priority': task.priority,
                'title': f'{task.priority.capitalize()} priority task pending',
                'message': task.title,
                'task_id': task.id,
            })

        type_order = {'error': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda x: type_order.get(x['type'], 3))

        return Response({
            'alerts': alerts,
            'count': len(alerts),
        })
