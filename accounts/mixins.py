class ScopeFilterMixin:
    """
    Mixin for DRF generic views that automatically filters querysets
    based on the logged-in user's role and organizational scope.

    Subclasses must define the field name mappings:
        scope_field_region   - FK field name for region filtering (e.g., 'region_scope')
        scope_field_team     - FK field name for team filtering (e.g., 'team_scope')
        scope_field_assigned - FK field name for self-filtering (e.g., 'assigned_to')

    Scope logic:
        Admin / Auditor      -> sees all records
        Regional Manager     -> sees records in their region
        Team Lead            -> sees records in their team
        Field Agent          -> sees only records assigned to them
        Unknown role         -> sees nothing
    """

    scope_field_region = None
    scope_field_team = None
    scope_field_assigned = None

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if not user.is_authenticated or not hasattr(user, 'profile'):
            return qs.none()

        role = user.profile.role.name

        if role in ('admin', 'auditor'):
            # Full visibility
            return qs

        elif role == 'regional_manager':
            if self.scope_field_region and user.profile.region:
                return qs.filter(**{self.scope_field_region: user.profile.region})
            return qs

        elif role == 'team_lead':
            if self.scope_field_team and user.profile.team:
                return qs.filter(**{self.scope_field_team: user.profile.team})
            return qs

        elif role == 'field_agent':
            if self.scope_field_assigned and user.profile:
                return qs.filter(**{self.scope_field_assigned: user.profile})
            return qs.none()

        # Unknown role - deny access
        return qs.none()
