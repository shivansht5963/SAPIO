from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Role, Region, Team, EmployeeProfile, ModuleAccess


class RoleSerializer(serializers.ModelSerializer):
    display = serializers.CharField(source='get_name_display', read_only=True)

    class Meta:
        model = Role
        fields = ('name', 'display')


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name')


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = fields


class ModuleAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleAccess
        fields = ('module_name', 'can_create', 'can_read', 'can_update', 'can_delete')


class EmployeeProfileSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    team = TeamSerializer(read_only=True)
    region = RegionSerializer(read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ('employee_id', 'phone', 'is_active', 'role', 'team', 'region')
        read_only_fields = fields


class MeResponseSerializer(serializers.Serializer):
    """Response shape for the /me/ endpoint."""
    user = UserProfileSerializer(read_only=True)
    profile = EmployeeProfileSerializer(read_only=True)
    permissions = ModuleAccessSerializer(many=True, read_only=True)
