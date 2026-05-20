from rest_framework.permissions import BasePermission
from .models import ModuleAccess


def check_module_access(user, module_name, action):
    """
    Check if a user has a specific permission on a module.

    Args:
        user: Django User instance
        module_name: str - one of 'tasks', 'visits', 'logs', 'reports', 'users'
        action: str - one of 'create', 'read', 'update', 'delete'

    Returns:
        bool - True if the user's role has the permission, False otherwise
    """
    if not user.is_authenticated:
        return False
    if not hasattr(user, 'profile'):
        return False

    try:
        access = ModuleAccess.objects.get(
            role=user.profile.role,
            module_name=module_name,
        )
        return getattr(access, f'can_{action}', False)
    except ModuleAccess.DoesNotExist:
        return False


def ModulePermission(module_name, action):
    """
    Factory function that returns a DRF permission class
    for a specific module + action combination.

    Usage in views:
        permission_classes = [IsAuthenticated, ModulePermission('tasks', 'create')]
    """
    class _ModulePermission(BasePermission):
        message = f"You do not have '{action}' permission for the '{module_name}' module."

        def has_permission(self, request, view):
            return check_module_access(request.user, module_name, action)

    # Give the class a readable name for debugging
    _ModulePermission.__name__ = f'ModulePermission_{module_name}_{action}'
    _ModulePermission.__qualname__ = _ModulePermission.__name__

    return _ModulePermission
