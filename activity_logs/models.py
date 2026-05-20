from django.db import models
from django.contrib.auth.models import User


# ── Action Choices ──
ACTION_CHOICES = [
    ('created', 'Created'),
    ('assigned', 'Assigned'),
    ('started', 'Started'),
    ('completed', 'Completed'),
    ('status_changed', 'Status Changed'),
    ('updated', 'Updated'),
]

# ── Entity Type Choices ──
ENTITY_TYPE_CHOICES = [
    ('task', 'Task'),
    ('visit', 'Visit'),
]


class ActivityLog(models.Model):
    """
    Audit trail for tracking important system actions.
    Auto-created when tasks/visits are created, assigned,
    started, completed, or have their status changed.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activity_logs',
    )
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    entity_type = models.CharField(max_length=20, choices=ENTITY_TYPE_CHOICES)
    entity_id = models.PositiveIntegerField()
    description = models.TextField(help_text="Human-readable log message")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'

    def __str__(self):
        return f"[{self.timestamp:%Y-%m-%d %H:%M}] {self.user.username} — {self.get_action_display()} {self.get_entity_type_display()} #{self.entity_id}"
