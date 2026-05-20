from rest_framework import serializers
from .models import Task
from accounts.models import EmployeeProfile, Team, Region

class MinimalEmployeeProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ('id', 'employee_id', 'username', 'first_name')

class MinimalTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('id', 'name')

class MinimalRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name', 'code')

class TaskListSerializer(serializers.ModelSerializer):
    assigned_to = MinimalEmployeeProfileSerializer(read_only=True)
    team_scope = MinimalTeamSerializer(read_only=True)
    region_scope = MinimalRegionSerializer(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'title', 'status', 'priority', 'due_date', 
            'assigned_to', 'team_scope', 'region_scope', 'created_at'
        )

class TaskDetailSerializer(TaskListSerializer):
    created_by = MinimalEmployeeProfileSerializer(read_only=True)

    class Meta(TaskListSerializer.Meta):
        fields = TaskListSerializer.Meta.fields + ('description', 'created_by', 'updated_at')

class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('title', 'description', 'status', 'priority', 'due_date', 'assigned_to')

    def validate(self, attrs):
        user = self.context['request'].user
        assigned_to = attrs.get('assigned_to')

        if not hasattr(user, 'profile'):
            raise serializers.ValidationError("User profile not found.")

        user_role = user.profile.role.name

        if assigned_to:
            # Ensure the assigned user is in the creator's scope if creator is Lead/Manager
            if user_role == 'regional_manager' and assigned_to.region != user.profile.region:
                raise serializers.ValidationError({"assigned_to": "Cannot assign to an agent outside your region."})
            if user_role == 'team_lead' and assigned_to.team != user.profile.team:
                raise serializers.ValidationError({"assigned_to": "Cannot assign to an agent outside your team."})
            if user_role == 'field_agent':
                 raise serializers.ValidationError("Field agents cannot assign tasks.")

        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['created_by'] = user.profile

        assigned_to = validated_data.get('assigned_to')
        if assigned_to:
            validated_data['team_scope'] = assigned_to.team
            validated_data['region_scope'] = assigned_to.region
        else:
            # If unassigned, set scope based on creator's scope
            validated_data['team_scope'] = user.profile.team
            validated_data['region_scope'] = user.profile.region

        return super().create(validated_data)

class TaskAssignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('assigned_to',)

    def validate_assigned_to(self, value):
         if not value:
              return value
         user = self.context['request'].user
         user_role = user.profile.role.name

         if user_role == 'regional_manager' and value.region != user.profile.region:
             raise serializers.ValidationError("Cannot assign to an agent outside your region.")
         if user_role == 'team_lead' and value.team != user.profile.team:
             raise serializers.ValidationError("Cannot assign to an agent outside your team.")
             
         return value
