from django.db import models
from django.contrib.auth.models import User


# ── Role Choices ──
ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('regional_manager', 'Regional Manager'),
    ('team_lead', 'Team Lead'),
    ('field_agent', 'Field Agent'),
    ('auditor', 'Auditor'),
]

# ── Module Choices ──
MODULE_CHOICES = [
    ('tasks', 'Tasks'),
    ('visits', 'Visits'),
    ('logs', 'Activity Logs'),
    ('reports', 'Reports'),
    ('users', 'User Management'),
]


class Role(models.Model):
    """Defines a job function/role in the system (Admin, Manager, etc.)."""

    name = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.get_name_display()


class Region(models.Model):
    """Geographical region/zone for scoping data visibility."""

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, help_text="Short code, e.g. NORTH, SOUTH")

    class Meta:
        ordering = ['name']
        verbose_name = 'Region'
        verbose_name_plural = 'Regions'

    def __str__(self):
        return self.name


class Team(models.Model):
    """A team that belongs to a region. Field agents are assigned to teams."""

    name = models.CharField(max_length=100)
    region = models.ForeignKey(
        Region,
        on_delete=models.CASCADE,
        related_name='teams',
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class ModuleAccess(models.Model):
    """
    Granular permission mapping: which Role can perform which
    CRUD actions on which module.
    """

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='permissions',
    )
    module_name = models.CharField(max_length=50, choices=MODULE_CHOICES)
    can_create = models.BooleanField(default=False)
    can_read = models.BooleanField(default=True)
    can_update = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)

    class Meta:
        unique_together = ('role', 'module_name')
        ordering = ['role', 'module_name']
        verbose_name = 'Module Access'
        verbose_name_plural = 'Module Access'

    def __str__(self):
        perms = []
        if self.can_create:
            perms.append('C')
        if self.can_read:
            perms.append('R')
        if self.can_update:
            perms.append('U')
        if self.can_delete:
            perms.append('D')
        return f"{self.role} → {self.get_module_name_display()} [{''.join(perms)}]"


class EmployeeProfile(models.Model):
    """
    Extends Django's built-in User model via OneToOne.
    Stores role, team/region scope, and employee metadata.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name='employees',
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
    )
    region = models.ForeignKey(
        Region,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees',
    )
    phone = models.CharField(max_length=15, blank=True)
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique employee identifier, e.g. EMP-001",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['employee_id']
        verbose_name = 'Employee Profile'
        verbose_name_plural = 'Employee Profiles'

    def __str__(self):
        return f"{self.user.username} ({self.role})"
