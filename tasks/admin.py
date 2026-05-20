from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'priority', 'assigned_to', 'due_date', 'team_scope', 'created_at')
    list_filter = ('status', 'priority', 'team_scope', 'region_scope')
    search_fields = ('title', 'description')
    raw_id_fields = ('created_by', 'assigned_to')
    date_hierarchy = 'created_at'
