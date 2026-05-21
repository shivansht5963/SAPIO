from django.db import models
from accounts.models import EmployeeProfile
from tasks.models import Task


# ── Visit Status Choices ──
VISIT_STATUS_CHOICES = [
    ('started', 'Started'),
    ('completed', 'Completed'),
]

# ── Risk Flag Choices ──
RISK_FLAG_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]


class Visit(models.Model):
    """
    A visit performed by a field agent for a specific task.
    Contains raw notes and AI-generated insights.
    """

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='visits',
    )
    started_by = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='visits',
    )
    status = models.CharField(
        max_length=20,
        choices=VISIT_STATUS_CHOICES,
        default='started',
    )
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    # ── Agent's raw notes ──
    visit_notes = models.TextField(blank=True)

    # ── AI generated fields ──
    ai_summary = models.TextField(blank=True)
    ai_recommendation = models.TextField(blank=True)
    ai_risk_flag = models.CharField(
        max_length=10,
        choices=RISK_FLAG_CHOICES,
        default='low',
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Visit'
        verbose_name_plural = 'Visits'

    def __str__(self):
        return f"Visit for '{self.task.title}' — {self.get_status_display()}"
