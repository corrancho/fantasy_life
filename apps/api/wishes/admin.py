from django.contrib import admin
from .models import Category, Wish, Match, Period, Assignment, Negotiation, Execution


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_adult', 'max_wishes_per_period', 'min_days_to_complete', 'max_days_to_complete', 'is_active')
    list_filter = ('is_adult', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Wish)
class WishAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'is_active', 'created_at')
    list_filter = ('category', 'is_active', 'created_at')
    search_fields = ('title', 'description', 'user__nickname')
    ordering = ('-created_at',)
    raw_id_fields = ('user',)


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'mode', 'status', 'created_at')
    list_filter = ('mode', 'status', 'created_at')
    search_fields = ('user1__nickname', 'user2__nickname')
    ordering = ('-created_at',)
    raw_id_fields = ('user1', 'user2')
    filter_horizontal = ('private_categories',)


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'match', 'is_active', 'created_at')
    list_filter = ('is_active', 'start_date')
    ordering = ('-start_date',)
    raw_id_fields = ('match',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('wish', 'assigned_to', 'period', 'due_date', 'is_completed', 'is_rejected')
    list_filter = ('is_completed', 'is_rejected', 'assigned_at')
    search_fields = ('wish__title', 'assigned_to__nickname')
    ordering = ('-assigned_at',)
    raw_id_fields = ('period', 'wish', 'assigned_to')


@admin.register(Negotiation)
class NegotiationAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'proposed_by', 'proposed_date', 'status', 'created_at')
    list_filter = ('status', 'proposed_date')
    search_fields = ('assignment__wish__title', 'proposed_by__nickname')
    ordering = ('-created_at',)
    raw_id_fields = ('assignment', 'proposed_by')


@admin.register(Execution)
class ExecutionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'completed_date', 'rating', 'created_at')
    list_filter = ('rating', 'completed_date')
    search_fields = ('assignment__wish__title',)
    ordering = ('-completed_date',)
    raw_id_fields = ('assignment',)
