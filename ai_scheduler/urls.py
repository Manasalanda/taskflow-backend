from django.urls import path
from .views import GenerateScheduleView, RescheduleView, PrioritySuggestionsView

urlpatterns = [
    path('generate-schedule/', GenerateScheduleView.as_view(), name='generate_schedule'),
    path('reschedule/', RescheduleView.as_view(), name='reschedule'),
    path('priority-suggestions/', PrioritySuggestionsView.as_view(), name='priority_suggestions'),
]