from django.contrib import admin
from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('task', 'started_by', 'status', 'start_time', 'end_time', 'ai_risk_flag')
    list_filter = ('status', 'ai_risk_flag')
    search_fields = ('task__title', 'visit_notes')
    raw_id_fields = ('task', 'started_by')
    date_hierarchy = 'start_time'
