from activity_logs.models import ActivityLog

def log_activity(user, action, entity_type, entity_id, description):
    """
    Utility to create an ActivityLog entry.
    """
    if not user or not user.is_authenticated:
        return None

    return ActivityLog.objects.create(
        user=user,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description
    )
