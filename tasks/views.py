from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from accounts.mixins import ScopeFilterMixin
from accounts.utils import ModulePermission
from .models import Task
from .serializers import (
    TaskListSerializer,
    TaskDetailSerializer,
    TaskCreateUpdateSerializer,
    TaskAssignSerializer
)
from services.activity_logger import log_activity

class TaskViewSet(ScopeFilterMixin, viewsets.ModelViewSet):
    """
    CRUD API for Tasks.
    Automatically filters Tasks based on user's role and scope (via ScopeFilterMixin).
    Enforces module-level RBAC via ModulePermission.
    """
    
    # Configure ScopeFilterMixin fields
    scope_field_region = 'region_scope'
    scope_field_team = 'team_scope'
    scope_field_assigned = 'assigned_to'

    queryset = Task.objects.all().select_related(
        'assigned_to__user', 'created_by__user', 'team_scope', 'region_scope'
    ).prefetch_related('visits__started_by__user')

    def get_permissions(self):
        """Map DRF actions to ModulePermission read/create/update/delete."""
        permissions = [IsAuthenticated()]
        
        if self.action in ['list', 'retrieve']:
            permissions.append(ModulePermission('tasks', 'read')())
        elif self.action == 'create':
            permissions.append(ModulePermission('tasks', 'create')())
        elif self.action in ['update', 'partial_update', 'assign']:
            permissions.append(ModulePermission('tasks', 'update')())
        elif self.action == 'destroy':
            permissions.append(ModulePermission('tasks', 'delete')())
            
        return permissions

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'retrieve':
            return TaskDetailSerializer
        elif self.action == 'assign':
            return TaskAssignSerializer
        return TaskCreateUpdateSerializer

    def perform_create(self, serializer):
        task = serializer.save()
        log_activity(
            user=self.request.user,
            action='created',
            entity_type='task',
            entity_id=task.id,
            description=f'Task "{task.title}" created.'
        )

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        task = serializer.save()
        
        # Scope update
        if 'assigned_to' in serializer.validated_data and task.assigned_to:
            task.team_scope = task.assigned_to.team
            task.region_scope = task.assigned_to.region
            task.save(update_fields=['team_scope', 'region_scope'])
            
        # Logging
        if 'status' in serializer.validated_data and old_status != task.status:
            log_activity(
                user=self.request.user,
                action='status_changed',
                entity_type='task',
                entity_id=task.id,
                description=f'Task status changed from {old_status} to {task.status}.'
            )

    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        """
        Special action to assign or reassign a task.
        """
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            
            assigned_profile = task.assigned_to
            assigned_name = assigned_profile.user.username if assigned_profile else "Unassigned"
            log_activity(
                user=request.user,
                action='assigned',
                entity_type='task',
                entity_id=task.id,
                description=f'Task assigned to {assigned_name}.'
            )
            
            return Response(TaskDetailSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
