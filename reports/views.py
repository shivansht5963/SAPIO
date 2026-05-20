from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta

from accounts.utils import ModulePermission
from tasks.models import Task
from visits.models import Visit
from activity_logs.models import ActivityLog
from activity_logs.serializers import ActivityLogSerializer


def get_task_scope(user):
    """
    Returns a queryset filter dict for Tasks based on the user's role.
    Admin/Auditor: all tasks
    Regional Manager: tasks in their region
    Team Lead: tasks in their team
    Field Agent: tasks assigned to them
    """
    if not hasattr(user, 'profile'):
        return {}  # superuser - no filter = all tasks

    role = user.profile.role.name

    if role in ['admin', 'auditor']:
        return {}
    elif role == 'regional_manager':
        return {'region_scope': user.profile.region}
    elif role == 'team_lead':
        return {'team_scope': user.profile.team}
    elif role == 'field_agent':
        return {'assigned_to': user.profile}
    return {}


def get_visit_scope(user):
    """
    Returns a queryset filter dict for Visits based on the user's role.
    """
    task_scope = get_task_scope(user)
    # Prefix with task__ for Visit filters
    return {f'task__{k}': v for k, v in task_scope.items()}


class PendingTasksReportView(APIView):
    """
    GET /api/reports/pending-tasks/
    Returns pending tasks grouped by region and team.
    Scoped to requesting user's role.
    """
    permission_classes = [IsAuthenticated, ModulePermission('reports', 'read')]

    def get(self, request):
        scope = get_task_scope(request.user)
        qs = Task.objects.filter(status='pending', **scope)

        data = (
            qs
            .values(
                region_name=F('region_scope__name'),
                team_name=F('team_scope__name'),
            )
            .annotate(pending_count=Count('id'))
            .order_by('region_name', 'team_name')
        )

        return Response(list(data))


class CompletionTimeReportView(APIView):
    """
    GET /api/reports/completion-time/
    Returns average visit completion time (minutes) per agent.
    Scoped to requesting user's role.
    """
    permission_classes = [IsAuthenticated, ModulePermission('reports', 'read')]

    def get(self, request):
        scope = get_visit_scope(request.user)
        qs = Visit.objects.filter(
            status='completed',
            end_time__isnull=False,
            **scope
        )

        # Annotate with duration in seconds, then convert
        qs = qs.annotate(
            duration=ExpressionWrapper(
                F('end_time') - F('start_time'),
                output_field=DurationField()
            )
        )

        # Group by agent
        from django.db.models import Avg
        agent_data = (
            qs
            .values(
                agent_username=F('started_by__user__username'),
                agent_employee_id=F('started_by__employee_id'),
            )
            .annotate(
                visit_count=Count('id'),
                avg_duration_seconds=Avg(
                    ExpressionWrapper(
                        F('end_time') - F('start_time'),
                        output_field=DurationField()
                    )
                )
            )
            .order_by('agent_username')
        )

        # Convert duration to minutes for readability
        result = []
        for row in agent_data:
            avg_sec = row['avg_duration_seconds']
            avg_minutes = round(avg_sec.total_seconds() / 60, 2) if avg_sec else 0
            result.append({
                'agent_username': row['agent_username'],
                'agent_employee_id': row['agent_employee_id'],
                'visit_count': row['visit_count'],
                'avg_completion_minutes': avg_minutes,
            })

        return Response(result)


class RecentVisitsReportView(APIView):
    """
    GET /api/reports/recent-visits/
    Returns visits completed in the last 7 days, grouped by date.
    Scoped to requesting user's role.
    """
    permission_classes = [IsAuthenticated, ModulePermission('reports', 'read')]

    def get(self, request):
        scope = get_visit_scope(request.user)
        seven_days_ago = timezone.now() - timedelta(days=7)

        qs = Visit.objects.filter(
            status='completed',
            end_time__gte=seven_days_ago,
            **scope
        )

        data = (
            qs
            .annotate(date=TruncDate('end_time'))
            .values('date')
            .annotate(completed_count=Count('id'))
            .order_by('date')
        )

        return Response(list(data))


class TaskDistributionReportView(APIView):
    """
    GET /api/reports/task-distribution/
    Returns task status counts grouped by region.
    Scoped to requesting user's role.
    """
    permission_classes = [IsAuthenticated, ModulePermission('reports', 'read')]

    def get(self, request):
        scope = get_task_scope(request.user)
        qs = Task.objects.filter(**scope)

        data = (
            qs
            .values(
                region_name=F('region_scope__name'),
                task_status=F('status'),
            )
            .annotate(count=Count('id'))
            .order_by('region_name', 'task_status')
        )

        return Response(list(data))


class DashboardView(APIView):
    """
    GET /api/reports/dashboard/
    Returns a comprehensive scoped summary:
    - Task counts by status
    - Visit counts (completed vs started)
    - High-risk visit count
    - Recent 5 activity logs
    """
    permission_classes = [IsAuthenticated, ModulePermission('reports', 'read')]

    def get(self, request):
        user = request.user
        task_scope = get_task_scope(user)
        visit_scope = get_visit_scope(user)

        # ── Task summary ──
        tasks = Task.objects.filter(**task_scope)
        task_summary = {
            'total': tasks.count(),
            'by_status': dict(
                tasks.values_list('status').annotate(count=Count('id'))
            ),
        }

        # ── Visit summary ──
        visits = Visit.objects.filter(**visit_scope)
        visit_summary = {
            'total': visits.count(),
            'completed': visits.filter(status='completed').count(),
            'started': visits.filter(status='started').count(),
            'high_risk': visits.filter(ai_risk_flag='high').count(),
        }

        # ── Recent activity (last 5 logs scoped by role) ──
        if not hasattr(user, 'profile'):
            log_qs = ActivityLog.objects.all()
        else:
            role = user.profile.role.name
            log_qs = ActivityLog.objects.all()
            if role == 'regional_manager':
                log_qs = log_qs.filter(user__profile__region=user.profile.region)
            elif role == 'team_lead':
                log_qs = log_qs.filter(user__profile__team=user.profile.team)
            elif role == 'field_agent':
                log_qs = log_qs.filter(user=user)

        recent_logs = ActivityLogSerializer(
            log_qs.select_related('user__profile__role').order_by('-timestamp')[:5],
            many=True
        ).data

        return Response({
            'tasks': task_summary,
            'visits': visit_summary,
            'recent_activity': recent_logs,
        })
