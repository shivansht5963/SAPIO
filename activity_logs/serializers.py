from rest_framework import serializers
from .models import ActivityLog
from accounts.models import EmployeeProfile

class MinimalEmployeeProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ('id', 'employee_id', 'username', 'first_name', 'role_name')

class ActivityLogSerializer(serializers.ModelSerializer):
    user_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = ActivityLog
        fields = ('id', 'user_profile', 'action', 'entity_type', 'entity_id', 'description', 'timestamp')

    def get_user_profile(self, obj):
        if hasattr(obj.user, 'profile'):
            return MinimalEmployeeProfileSerializer(obj.user.profile).data
        return {'username': obj.user.username}
