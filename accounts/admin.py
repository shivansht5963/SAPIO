from django.contrib import admin
from .models import Role, Region, Team, ModuleAccess, EmployeeProfile


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')
    search_fields = ('name', 'code')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'region')
    list_filter = ('region',)
    search_fields = ('name',)


@admin.register(ModuleAccess)
class ModuleAccessAdmin(admin.ModelAdmin):
    list_display = ('role', 'module_name', 'can_create', 'can_read', 'can_update', 'can_delete')
    list_filter = ('role', 'module_name')
    list_editable = ('can_create', 'can_read', 'can_update', 'can_delete')


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'employee_id', 'role', 'team', 'region', 'is_active')
    list_filter = ('role', 'is_active', 'region', 'team')
    search_fields = ('user__username', 'user__email', 'employee_id')
    raw_id_fields = ('user',)
