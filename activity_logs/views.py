from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from accounts.utils import ModulePermission
from .models import ActivityLog
from .serializers import ActivityLogSerializer

class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only API for Activity Logs.
    Scoped to the user's role:
    - Admin/Auditor: All logs
    - Regional Manager: Logs from their region
    - Team Lead: Logs from their team
    - Field Agent: No access (enforced by ModulePermission)
    """
    serializer_class = ActivityLogSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entity_type', 'action', 'user__id']
    
    def get_permissions(self):
        return [IsAuthenticated(), ModulePermission('logs', 'read')()]

    def get_queryset(self):
        user = self.request.user
        qs = ActivityLog.objects.all().select_related('user__profile__role')
        
        # If no profile, they are a superuser, they see all
        if not hasattr(user, 'profile'):
            return qs
            
        role_name = user.profile.role.name
        
        if role_name in ['admin', 'auditor']:
            return qs
        elif role_name == 'regional_manager':
            # See logs for users in their region
            return qs.filter(user__profile__region=user.profile.region)
        elif role_name == 'team_lead':
            # See logs for users in their team
            return qs.filter(user__profile__team=user.profile.team)
            
        # Field agents shouldn't even reach here due to ModulePermission, but fallback:
        return qs.none()
