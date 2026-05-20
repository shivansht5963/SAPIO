from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Allows access only to users with the Admin role."""
    message = "Only Admin users can perform this action."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.role.name == 'admin'


class IsManagerOrAbove(BasePermission):
    """Allows access to Admin and Regional Manager roles."""
    message = "Only Admin or Regional Manager can perform this action."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.role.name in ('admin', 'regional_manager')


class IsLeadOrAbove(BasePermission):
    """Allows access to Admin, Regional Manager, and Team Lead roles."""
    message = "Only Admin, Regional Manager, or Team Lead can perform this action."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.role.name in ('admin', 'regional_manager', 'team_lead')


class IsFieldAgent(BasePermission):
    """Allows access only to Field Agent role."""
    message = "Only Field Agents can perform this action."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.role.name == 'field_agent'


class IsAuditor(BasePermission):
    """Allows access only to Auditor role (read-only by design)."""
    message = "Only Auditors can access this resource."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not hasattr(request.user, 'profile'):
            return False
        return request.user.profile.role.name == 'auditor'


class IsReadOnly(BasePermission):
    """Allows only safe HTTP methods (GET, HEAD, OPTIONS)."""
    message = "This resource is read-only."

    def has_permission(self, request, view):
        return request.method in ('GET', 'HEAD', 'OPTIONS')
