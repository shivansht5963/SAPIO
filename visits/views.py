from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from accounts.mixins import ScopeFilterMixin
from accounts.utils import ModulePermission
from .models import Visit
from .serializers import (
    VisitListSerializer,
    VisitDetailSerializer,
    VisitStartSerializer,
    VisitCompleteSerializer
)

class VisitViewSet(ScopeFilterMixin, viewsets.ModelViewSet):
    """
    CRUD API for Visits.
    ScopeFilterMixin is configured to use the related Task's scope fields.
    """
    
    # Configure ScopeFilterMixin fields to use related task
    scope_field_region = 'task__region_scope'
    scope_field_team = 'task__team_scope'
    scope_field_assigned = 'task__assigned_to'

    queryset = Visit.objects.all().select_related(
        'task__assigned_to', 
        'task__team_scope', 
        'task__region_scope',
        'started_by__user'
    )

    def get_permissions(self):
        permissions = [IsAuthenticated()]
        
        if self.action in ['list', 'retrieve']:
            permissions.append(ModulePermission('visits', 'read')())
        elif self.action == 'start':
            permissions.append(ModulePermission('visits', 'create')())
        elif self.action in ['update', 'partial_update', 'complete']:
            permissions.append(ModulePermission('visits', 'update')())
        elif self.action == 'destroy':
            permissions.append(ModulePermission('visits', 'delete')())
            
        return permissions

    def get_serializer_class(self):
        if self.action == 'list':
            return VisitListSerializer
        elif self.action == 'retrieve':
            return VisitDetailSerializer
        elif self.action == 'start':
            return VisitStartSerializer
        elif self.action == 'complete':
            return VisitCompleteSerializer
        # Default fallback, though standard create/update aren't the main workflow for Visits
        return VisitDetailSerializer

    @action(detail=False, methods=['post'])
    def start(self, request):
        """
        Start a new visit for a task.
        Expects {"task_id": 1} in the request body.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            visit = serializer.save()
            from services.activity_logger import log_activity
            log_activity(
                user=request.user,
                action='started',
                entity_type='visit',
                entity_id=visit.id,
                description=f'Visit started for task {visit.task.id}.'
            )
            return Response(VisitDetailSerializer(visit).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Complete an ongoing visit.
        Expects {"visit_notes": "..."} in the request body.
        """
        visit = self.get_object()
        serializer = self.get_serializer(visit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            from services.activity_logger import log_activity
            log_activity(
                user=request.user,
                action='completed',
                entity_type='visit',
                entity_id=visit.id,
                description=f'Visit completed for task {visit.task.id}.'
            )
            return Response(VisitDetailSerializer(visit).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
