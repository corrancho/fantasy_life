from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Category(models.Model):
    """Global wish categories with their own rules."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_adult = models.BooleanField(default=False, help_text="Restricted to users 18+")
    max_wishes_per_period = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Maximum wishes that can be assigned from this category per period"
    )
    min_days_to_complete = models.IntegerField(
        default=7,
        validators=[MinValueValidator(1)],
        help_text="Minimum days given to complete a wish from this category"
    )
    max_days_to_complete = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        help_text="Maximum days allowed to complete a wish from this category"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} {'(18+)' if self.is_adult else ''}"


class Wish(models.Model):
    """User wishes that can be assigned to matched users."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishes'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='wishes'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive wishes won't be assigned"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wishes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['category', 'is_active']),
        ]

    def __str__(self):
        return f"{self.title} ({self.user.nickname})"


class Match(models.Model):
    """Connections between users for wish exchange."""
    MODE_PRIVATE = 'private'
    MODE_PUBLIC = 'public'
    MODE_CHOICES = [
        (MODE_PRIVATE, 'Private (Couple)'),
        (MODE_PUBLIC, 'Public (Network)'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_BLOCKED = 'blocked'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_BLOCKED, 'Blocked'),
    ]

    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matches_as_user1'
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matches_as_user2'
    )
    mode = models.CharField(max_length=10, choices=MODE_CHOICES)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    # Private mode settings (agreed upon by both users)
    private_categories = models.ManyToManyField(
        Category,
        blank=True,
        help_text="Categories agreed upon for private matches"
    )
    private_period_days = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        help_text="Custom period length for private matches (in days)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matches'
        unique_together = [['user1', 'user2']]
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user1', 'status']),
            models.Index(fields=['user2', 'status']),
        ]

    def __str__(self):
        return f"{self.user1.nickname} ↔ {self.user2.nickname} ({self.get_mode_display()})"

    def save(self, *args, **kwargs):
        # Ensure user1.id < user2.id for consistency
        if self.user1_id and self.user2_id and self.user1_id > self.user2_id:
            self.user1, self.user2 = self.user2, self.user1
        super().save(*args, **kwargs)


class Period(models.Model):
    """Time periods for wish assignments (default monthly)."""
    match = models.ForeignKey(
        Match,
        on_delete=models.CASCADE,
        related_name='periods',
        null=True,
        blank=True,
        help_text="Specific match for private periods, null for global public periods"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'periods'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['start_date', 'end_date', 'is_active']),
            models.Index(fields=['match', 'is_active']),
        ]

    def __str__(self):
        match_str = f" ({self.match})" if self.match else " (Global)"
        return f"Period {self.start_date} to {self.end_date}{match_str}"


class Assignment(models.Model):
    """Random wish assignments during a period."""
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    wish = models.ForeignKey(
        Wish,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assigned_wishes',
        help_text="User who must fulfill this wish"
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(
        help_text="Date by which the wish should be completed"
    )
    is_completed = models.BooleanField(default=False)
    is_rejected = models.BooleanField(
        default=False,
        help_text="True if rejected in public mode"
    )

    class Meta:
        db_table = 'assignments'
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['assigned_to', 'is_completed']),
            models.Index(fields=['period', 'is_completed']),
            models.Index(fields=['wish']),
        ]

    def __str__(self):
        return f"{self.wish.title} → {self.assigned_to.nickname}"


class Negotiation(models.Model):
    """Date/time negotiation for wish fulfillment."""
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    assignment = models.ForeignKey(
        Assignment,
        on_delete=models.CASCADE,
        related_name='negotiations'
    )
    proposed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='proposed_negotiations'
    )
    proposed_date = models.DateField()
    proposed_time = models.TimeField(null=True, blank=True)
    message = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    response_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'negotiations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['assignment', 'status']),
        ]

    def __str__(self):
        return f"Negotiation for {self.assignment} on {self.proposed_date}"


class Execution(models.Model):
    """Completed wishes with ratings and comments."""
    assignment = models.OneToOneField(
        Assignment,
        on_delete=models.CASCADE,
        related_name='execution'
    )
    completed_date = models.DateField()
    completed_time = models.TimeField(null=True, blank=True)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    comment_by_creator = models.TextField(
        blank=True,
        help_text="Comment by the wish creator"
    )
    comment_by_executor = models.TextField(
        blank=True,
        help_text="Comment by the user who fulfilled the wish"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'executions'
        ordering = ['-completed_date']
        indexes = [
            models.Index(fields=['assignment']),
            models.Index(fields=['completed_date']),
        ]

    def __str__(self):
        return f"Execution of {self.assignment} - {self.rating}★"

    def save(self, *args, **kwargs):
        # Mark assignment as completed
        self.assignment.is_completed = True
        self.assignment.save()
        super().save(*args, **kwargs)
