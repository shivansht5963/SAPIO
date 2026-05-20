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
    )

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

    def perform_update(self, serializer):
        # We also need to update the scope fields if the assigned user changes on update
        task = serializer.save()
        if 'assigned_to' in serializer.validated_data and task.assigned_to:
            task.team_scope = task.assigned_to.team
            task.region_scope = task.assigned_to.region
            task.save(update_fields=['team_scope', 'region_scope'])

    @action(detail=True, methods=['patch'])
    def assign(self, request, pk=None):
        """
        Special action to assign or reassign a task.
        """
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(TaskDetailSerializer(task).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
