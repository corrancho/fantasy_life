from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count, Avg, F, ExpressionWrapper, fields as django_fields
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import random

from .models import Category, Wish, Match, Period, Assignment, Negotiation, Execution
from .serializers import (
    CategorySerializer, WishSerializer, MatchSerializer,
    PeriodSerializer, AssignmentSerializer, NegotiationSerializer,
    ExecutionSerializer, RankingSerializer
)
from .permissions import IsOwnerOrReadOnly, IsMatchParticipant

User = get_user_model()


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Categories are read-only for users.
    Filtered by age restrictions.
    """
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Category.objects.filter(is_active=True)
        
        # Filter adult content for minors
        if not user.is_adult:
            queryset = queryset.filter(is_adult=False)
        
        return queryset


class WishViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for user wishes.
    Users can only manage their own wishes.
    """
    serializer_class = WishSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Wish.objects.filter(user=user).select_related('category', 'user')

    def perform_create(self, serializer):
        category = serializer.validated_data['category']
        
        # Validate category is not adult if user is minor
        if category.is_adult and not self.request.user.is_adult:
            raise permissions.PermissionDenied("You must be 18+ to create wishes in adult categories")
        
        serializer.save(user=self.request.user)


class MatchViewSet(viewsets.ModelViewSet):
    """
    Manage matches between users.
    Users can create, accept, reject, or block matches.
    """
    serializer_class = MatchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Match.objects.filter(
            Q(user1=user) | Q(user2=user)
        ).select_related('user1', 'user2')

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a pending match."""
        match = self.get_object()
        
        if match.status != Match.STATUS_PENDING:
            return Response(
                {'error': 'Match is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        match.status = Match.STATUS_ACCEPTED
        match.save()
        
        return Response({'status': 'Match accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a pending match."""
        match = self.get_object()
        
        if match.status != Match.STATUS_PENDING:
            return Response(
                {'error': 'Match is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        match.status = Match.STATUS_REJECTED
        match.save()
        
        return Response({'status': 'Match rejected'})

    @action(detail=True, methods=['post'])
    def block(self, request, pk=None):
        """Block a user."""
        match = self.get_object()
        match.status = Match.STATUS_BLOCKED
        match.save()
        
        return Response({'status': 'User blocked'})


class AssignmentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View assignments.
    Users can see wishes assigned to them or wishes they created that were assigned.
    """
    serializer_class = AssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Assignment.objects.filter(
            Q(assigned_to=user) | Q(wish__user=user)
        ).select_related(
            'wish', 'wish__user', 'wish__category', 'assigned_to', 'period'
        )

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject an assignment (only in public mode).
        """
        assignment = self.get_object()
        
        # Check if assignment is from a public match
        period = assignment.period
        if period.match and period.match.mode == Match.MODE_PRIVATE:
            return Response(
                {'error': 'Cannot reject wishes in private mode'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if assignment.assigned_to != request.user:
            return Response(
                {'error': 'You can only reject wishes assigned to you'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        assignment.is_rejected = True
        assignment.save()
        
        return Response({'status': 'Assignment rejected'})


class NegotiationViewSet(viewsets.ModelViewSet):
    """
    Date/time negotiation for wish fulfillment.
    """
    serializer_class = NegotiationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Negotiation.objects.filter(
            Q(assignment__assigned_to=user) | Q(assignment__wish__user=user)
        ).select_related(
            'assignment', 'assignment__wish', 'assignment__assigned_to', 'proposed_by'
        )

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        """Accept a negotiation proposal."""
        negotiation = self.get_object()
        
        if negotiation.status != Negotiation.STATUS_PENDING:
            return Response(
                {'error': 'Negotiation is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response_message = request.data.get('response_message', '')
        negotiation.status = Negotiation.STATUS_ACCEPTED
        negotiation.response_message = response_message
        negotiation.save()
        
        return Response({'status': 'Negotiation accepted'})

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a negotiation proposal."""
        negotiation = self.get_object()
        
        if negotiation.status != Negotiation.STATUS_PENDING:
            return Response(
                {'error': 'Negotiation is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        response_message = request.data.get('response_message', '')
        negotiation.status = Negotiation.STATUS_REJECTED
        negotiation.response_message = response_message
        negotiation.save()
        
        return Response({'status': 'Negotiation rejected'})


class ExecutionViewSet(viewsets.ModelViewSet):
    """
    Record wish executions with ratings.
    """
    serializer_class = ExecutionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Execution.objects.filter(
            Q(assignment__assigned_to=user) | Q(assignment__wish__user=user)
        ).select_related(
            'assignment', 'assignment__wish', 'assignment__assigned_to'
        )


class RankingsViewSet(viewsets.ViewSet):
    """
    View global rankings.
    """
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def most_completed(self, request):
        """Users with most completed wishes."""
        rankings = User.objects.annotate(
            total_completed=Count(
                'assigned_wishes',
                filter=Q(assigned_wishes__is_completed=True)
            )
        ).filter(
            total_completed__gt=0
        ).order_by('-total_completed')[:100]
        
        serializer = RankingSerializer(rankings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def best_rated(self, request):
        """Users with best average rating."""
        rankings = User.objects.annotate(
            average_rating=Avg(
                'assigned_wishes__execution__rating',
                filter=Q(assigned_wishes__is_completed=True)
            )
        ).filter(
            average_rating__isnull=False
        ).order_by('-average_rating')[:100]
        
        serializer = RankingSerializer(rankings, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def fastest_completion(self, request):
        """Users with fastest average completion time."""
        rankings = User.objects.annotate(
            average_completion_days=Avg(
                ExpressionWrapper(
                    F('assigned_wishes__execution__completed_date') - F('assigned_wishes__assigned_at'),
                    output_field=django_fields.DurationField()
                ),
                filter=Q(assigned_wishes__is_completed=True)
            )
        ).filter(
            average_completion_days__isnull=False
        ).order_by('average_completion_days')[:100]
        
        serializer = RankingSerializer(rankings, many=True)
        return Response(serializer.data)
