from django.urls import path
from .views import (
    PendingTasksReportView,
    CompletionTimeReportView,
    RecentVisitsReportView,
    TaskDistributionReportView,
    DashboardView,
)

urlpatterns = [
    path('reports/pending-tasks/', PendingTasksReportView.as_view(), name='report-pending-tasks'),
    path('reports/completion-time/', CompletionTimeReportView.as_view(), name='report-completion-time'),
    path('reports/recent-visits/', RecentVisitsReportView.as_view(), name='report-recent-visits'),
    path('reports/task-distribution/', TaskDistributionReportView.as_view(), name='report-task-distribution'),
    path('reports/dashboard/', DashboardView.as_view(), name='report-dashboard'),
]
