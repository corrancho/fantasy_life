from rest_framework import serializers
from .models import Category, Wish, Match, Period, Assignment, Negotiation, Execution
from users.serializers import UserSerializer


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'description', 'is_adult', 'max_wishes_per_period',
                  'min_days_to_complete', 'max_days_to_complete', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')


class WishSerializer(serializers.ModelSerializer):
    """Serializer for Wish model."""
    user = UserSerializer(read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Wish
        fields = ('id', 'user', 'category', 'category_name', 'title', 
                  'description', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MatchSerializer(serializers.ModelSerializer):
    """Serializer for Match model."""
    user1 = UserSerializer(read_only=True)
    user2 = UserSerializer(read_only=True)
    mode_display = serializers.CharField(source='get_mode_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Match
        fields = ('id', 'user1', 'user2', 'mode', 'mode_display', 'status', 
                  'status_display', 'private_categories', 'private_period_days',
                  'created_at', 'updated_at')
        read_only_fields = ('id', 'user1', 'created_at', 'updated_at')


class PeriodSerializer(serializers.ModelSerializer):
    """Serializer for Period model."""
    
    class Meta:
        model = Period
        fields = ('id', 'match', 'start_date', 'end_date', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model."""
    wish = WishSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    period_start = serializers.DateField(source='period.start_date', read_only=True)
    period_end = serializers.DateField(source='period.end_date', read_only=True)
    
    class Meta:
        model = Assignment
        fields = ('id', 'period', 'period_start', 'period_end', 'wish', 
                  'assigned_to', 'assigned_at', 'due_date', 'is_completed', 'is_rejected')
        read_only_fields = ('id', 'wish', 'assigned_to', 'assigned_at', 'due_date')


class NegotiationSerializer(serializers.ModelSerializer):
    """Serializer for Negotiation model."""
    proposed_by = UserSerializer(read_only=True)
    assignment_wish_title = serializers.CharField(source='assignment.wish.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Negotiation
        fields = ('id', 'assignment', 'assignment_wish_title', 'proposed_by', 
                  'proposed_date', 'proposed_time', 'message', 'status', 
                  'status_display', 'response_message', 'created_at', 'updated_at')
        read_only_fields = ('id', 'proposed_by', 'created_at', 'updated_at')

    def create(self, validated_data):
        validated_data['proposed_by'] = self.context['request'].user
        return super().create(validated_data)


class ExecutionSerializer(serializers.ModelSerializer):
    """Serializer for Execution model."""
    assignment = AssignmentSerializer(read_only=True)
    assignment_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Execution
        fields = ('id', 'assignment', 'assignment_id', 'completed_date', 
                  'completed_time', 'rating', 'comment_by_creator', 
                  'comment_by_executor', 'created_at')
        read_only_fields = ('id', 'created_at')

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value


class RankingSerializer(serializers.Serializer):
    """Serializer for user rankings."""
    user = UserSerializer(read_only=True)
    total_completed = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    average_completion_days = serializers.FloatField(read_only=True)