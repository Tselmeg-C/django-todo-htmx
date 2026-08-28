from datetime import UTC, datetime, timedelta

from django.template.defaultfilters import date as date_filter
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from todos.models import Todo


class TodoListViewTests(TestCase):
    def test_home_renders_active_and_resolved_sections_with_partials(self):
        active = Todo.objects.create(title="Active item")
        resolved = Todo.objects.create(title="Resolved item")
        resolved.resolve()

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "todos/home.html")
        self.assertTemplateUsed(response, "todos/partials/todo_sections.html")
        self.assertTemplateUsed(response, "todos/partials/todo_list.html")
        self.assertTemplateUsed(response, "todos/partials/todo_item.html")
        self.assertContains(response, "Active TODOs")
        self.assertContains(response, "Resolved TODOs")
        self.assertQuerySetEqual(response.context["active_todos"], [active])
        self.assertQuerySetEqual(response.context["resolved_todos"], [resolved])

    def test_active_todos_are_ordered_by_urgency_due_date_and_creation(self):
        today = timezone.localdate()
        base_time = datetime(2026, 8, 28, 9, 0, tzinfo=UTC)
        overdue_oldest = Todo.objects.create(
            title="Oldest overdue",
            due_date=today - timedelta(days=5),
        )
        overdue_newer = Todo.objects.create(
            title="Newer overdue",
            due_date=today - timedelta(days=1),
        )
        due_today = Todo.objects.create(title="Due today", due_date=today)
        future_older = Todo.objects.create(
            title="Future older",
            due_date=today + timedelta(days=2),
        )
        future_newer = Todo.objects.create(
            title="Future newer",
            due_date=today + timedelta(days=2),
        )
        undated_older = Todo.objects.create(title="Undated older")
        undated_newer = Todo.objects.create(title="Undated newer")
        Todo.objects.filter(pk=future_older.pk).update(created_at=base_time)
        Todo.objects.filter(pk=future_newer.pk).update(
            created_at=base_time + timedelta(minutes=1)
        )
        Todo.objects.filter(pk=undated_older.pk).update(created_at=base_time)
        Todo.objects.filter(pk=undated_newer.pk).update(
            created_at=base_time + timedelta(minutes=1)
        )

        response = self.client.get(reverse("home"))

        self.assertQuerySetEqual(
            response.context["active_todos"],
            [
                overdue_oldest,
                overdue_newer,
                due_today,
                future_newer,
                future_older,
                undated_newer,
                undated_older,
            ],
        )

    def test_resolved_todos_are_ordered_by_latest_resolution(self):
        earlier = Todo.objects.create(title="Resolved earlier")
        later = Todo.objects.create(title="Resolved later")
        earlier_time = datetime(2026, 8, 27, 12, 0, tzinfo=UTC)
        later_time = datetime(2026, 8, 28, 12, 0, tzinfo=UTC)
        Todo.objects.filter(pk=earlier.pk).update(
            is_resolved=True,
            resolved_at=earlier_time,
        )
        Todo.objects.filter(pk=later.pk).update(
            is_resolved=True,
            resolved_at=later_time,
        )

        response = self.client.get(reverse("home"))

        self.assertQuerySetEqual(response.context["resolved_todos"], [later, earlier])

    def test_todo_renders_present_optional_values_and_semantic_due_date(self):
        due_date = timezone.localdate() + timedelta(days=2)
        Todo.objects.create(
            title="Document release",
            description="Write notes\nShare notes",
            due_date=due_date,
        )

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Document release")
        self.assertContains(response, "Write notes<br>Share notes", html=True)
        self.assertContains(response, f'datetime="{due_date.isoformat()}"')
        self.assertContains(response, date_filter(due_date, "M j, Y"))
        self.assertNotContains(response, "No description")
        self.assertNotContains(response, "No due date")

    def test_only_overdue_active_todo_receives_overdue_cues(self):
        today = timezone.localdate()
        Todo.objects.create(
            title="Past active",
            due_date=today - timedelta(days=1),
        )
        Todo.objects.create(title="Due today", due_date=today)
        Todo.objects.create(title="Undated")
        resolved = Todo.objects.create(
            title="Past resolved",
            due_date=today - timedelta(days=1),
        )
        resolved.resolve()

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Overdue", count=1)
        self.assertContains(response, "todo-card--overdue", count=1)
        self.assertContains(response, "todo-card--resolved", count=1)
        self.assertContains(
            response,
            '<span class="status-badge status-badge--resolved">Resolved</span>',
            count=1,
            html=True,
        )

    def test_empty_states_are_independent(self):
        response = self.client.get(reverse("home"))

        self.assertContains(response, "No active TODOs yet.")
        self.assertContains(response, "No resolved TODOs yet.")

        active = Todo.objects.create(title="Only active")
        response = self.client.get(reverse("home"))

        self.assertContains(response, active.title)
        self.assertNotContains(response, "No active TODOs yet.")
        self.assertContains(response, "No resolved TODOs yet.")

        active.resolve()
        response = self.client.get(reverse("home"))

        self.assertContains(response, active.title)
        self.assertContains(response, "No active TODOs yet.")
        self.assertNotContains(response, "No resolved TODOs yet.")
