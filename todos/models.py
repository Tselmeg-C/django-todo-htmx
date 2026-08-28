from django.db import models
from django.utils import timezone


class Todo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(blank=True, null=True)
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(is_resolved=False, resolved_at__isnull=True)
                    | models.Q(is_resolved=True, resolved_at__isnull=False)
                ),
                name="todo_resolution_state_consistent",
            )
        ]

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        return (
            not self.is_resolved
            and self.due_date is not None
            and self.due_date < timezone.localdate()
        )

    def resolve(self):
        """Resolve this TODO once while preserving the first resolution time."""
        if self.is_resolved:
            return

        self.is_resolved = True
        self.resolved_at = timezone.now()
        self.save()

    def reopen(self):
        """Return this TODO to the active state."""
        if not self.is_resolved:
            return

        self.is_resolved = False
        self.resolved_at = None
        self.save()
