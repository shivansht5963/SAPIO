from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'entity_type', 'entity_id', 'description')
    list_filter = ('action', 'entity_type')
    search_fields = ('user__username', 'description')
    date_hierarchy = 'timestamp'

    # Logs are read-only — no manual creation or editing
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
