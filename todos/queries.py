from django.db.models import Case, IntegerField, Value, When
from django.utils import timezone

from todos.models import Todo


def active_todos():
    """Return active TODOs ordered by urgency and creation time."""
    today = timezone.localdate()
    due_group = Case(
        When(due_date__lt=today, then=Value(0)),
        When(due_date__isnull=False, then=Value(1)),
        default=Value(2),
        output_field=IntegerField(),
    )

    return (
        Todo.objects.filter(is_resolved=False)
        .annotate(_due_group=due_group)
        .order_by("_due_group", "due_date", "-created_at")
    )


def resolved_todos():
    """Return resolved TODOs with the most recently resolved first."""
    return Todo.objects.filter(is_resolved=True).order_by(
        "-resolved_at",
        "-created_at",
    )
