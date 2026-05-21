from rest_framework import serializers
from django.utils import timezone
from .models import Visit
from tasks.models import Task
from accounts.models import EmployeeProfile
from services.ai_service import AIService

class MinimalEmployeeProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)

    class Meta:
        model = EmployeeProfile
        fields = ('id', 'employee_id', 'username', 'first_name')

class MinimalTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'status', 'priority', 'due_date')

class VisitListSerializer(serializers.ModelSerializer):
    task = MinimalTaskSerializer(read_only=True)
    started_by = MinimalEmployeeProfileSerializer(read_only=True)

    class Meta:
        model = Visit
        fields = ('id', 'task', 'started_by', 'status', 'start_time', 'end_time', 'ai_risk_flag')

class VisitDetailSerializer(VisitListSerializer):
    class Meta(VisitListSerializer.Meta):
        fields = VisitListSerializer.Meta.fields + ('visit_notes', 'ai_summary', 'ai_recommendation', 'created_at')

class VisitStartSerializer(serializers.Serializer):
    """
    Serializer to handle starting a visit. 
    Accepts task_id and validates if the user can start it.
    """
    task_id = serializers.IntegerField()

    def validate_task_id(self, value):
        user = self.context['request'].user
        try:
            task = Task.objects.get(id=value)
        except Task.DoesNotExist:
            raise serializers.ValidationError("Task does not exist.")

        if not hasattr(user, 'profile'):
            raise serializers.ValidationError("User profile not found.")

        # Validate that the task is assigned to the current agent
        if task.assigned_to != user.profile:
            raise serializers.ValidationError("You can only start visits for tasks assigned to you.")

        # Ensure the task isn't already completed/cancelled
        if task.status in ['completed', 'cancelled']:
            raise serializers.ValidationError(f"Cannot start visit. Task is already {task.status}.")
            
        # Check if a Visit already exists and is active for this task
        # Optional: You might allow multiple visits per task, but for FFMS, let's assume 1 active visit at a time
        active_visits = Visit.objects.filter(task=task, status='started').exists()
        if active_visits:
            raise serializers.ValidationError("An active visit already exists for this task.")

        return value

    def create(self, validated_data):
        user = self.context['request'].user
        task_id = validated_data['task_id']
        task = Task.objects.get(id=task_id)

        # Create the visit
        visit = Visit.objects.create(
            task=task,
            started_by=user.profile,
            status='started',
            start_time=timezone.now()
        )

        # Update task status if it's currently pending
        if task.status == 'pending':
            task.status = 'in_progress'
            task.save(update_fields=['status'])

        return visit

class VisitCompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visit
        fields = ('visit_notes',)
        extra_kwargs = {
            'visit_notes': {'required': True, 'allow_blank': False}
        }

    def validate(self, attrs):
        if self.instance.status == 'completed':
            raise serializers.ValidationError("This visit is already completed.")
        return attrs

    def update(self, instance, validated_data):
        notes = validated_data.get('visit_notes')
        
        # Call the AI Service
        ai_insights = AIService.generate_insights(notes)

        instance.visit_notes = notes
        instance.status = 'completed'
        instance.end_time = timezone.now()
        instance.ai_summary = ai_insights['summary']
        instance.ai_recommendation = ai_insights['recommendation']
        instance.ai_risk_flag = ai_insights['risk_flag'].lower()
        
        instance.save()
        return instance
