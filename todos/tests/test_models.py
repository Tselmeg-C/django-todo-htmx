from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from todos.models import Todo


class TodoModelTests(TestCase):
    def test_new_todo_defaults_to_active_with_timestamps(self):
        todo = Todo.objects.create(title="Write tests")

        self.assertFalse(todo.is_resolved)
        self.assertIsNone(todo.resolved_at)
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)
        self.assertGreaterEqual(todo.updated_at, todo.created_at)
        self.assertEqual(str(todo), "Write tests")

    def test_resolve_records_first_resolution_time_and_is_idempotent(self):
        todo = Todo.objects.create(title="Ship feature")
        first_resolution = datetime(2026, 8, 28, 10, 30, tzinfo=UTC)
        later_time = first_resolution + timedelta(hours=1)

        with patch("todos.models.timezone.now", return_value=first_resolution):
            todo.resolve()

        todo.refresh_from_db()
        self.assertTrue(todo.is_resolved)
        self.assertEqual(todo.resolved_at, first_resolution)

        with patch("todos.models.timezone.now", return_value=later_time):
            todo.resolve()

        todo.refresh_from_db()
        self.assertEqual(todo.resolved_at, first_resolution)

    def test_reopen_clears_resolution_time_and_is_idempotent(self):
        todo = Todo.objects.create(title="Review feature")
        todo.resolve()

        todo.reopen()

        todo.refresh_from_db()
        self.assertFalse(todo.is_resolved)
        self.assertIsNone(todo.resolved_at)
        reopened_update_time = todo.updated_at

        todo.reopen()

        todo.refresh_from_db()
        self.assertEqual(todo.updated_at, reopened_update_time)

    def test_database_rejects_resolved_todo_without_resolution_time(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Todo.objects.create(title="Invalid", is_resolved=True)

    def test_database_rejects_active_todo_with_resolution_time(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Todo.objects.create(
                title="Invalid",
                is_resolved=False,
                resolved_at=timezone.now(),
            )

    def test_overdue_uses_local_date_and_active_state(self):
        today = timezone.localdate()

        overdue = Todo(title="Overdue", due_date=today - timedelta(days=1))
        due_today = Todo(title="Today", due_date=today)
        future = Todo(title="Future", due_date=today + timedelta(days=1))
        undated = Todo(title="Undated")
        resolved = Todo(
            title="Resolved",
            due_date=today - timedelta(days=1),
            is_resolved=True,
            resolved_at=timezone.now(),
        )

        self.assertTrue(overdue.is_overdue)
        self.assertFalse(due_today.is_overdue)
        self.assertFalse(future.is_overdue)
        self.assertFalse(undated.is_overdue)
        self.assertFalse(resolved.is_overdue)
