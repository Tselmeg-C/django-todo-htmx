from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from todos.models import Todo

HTMX_HEADERS = {"HTTP_HX_REQUEST": "true"}


class TodoJourneyRegressionTests(TestCase):
    def test_home_exposes_accessible_structure_and_all_primary_controls(self):
        active = Todo.objects.create(
            title="Review launch plan",
            description="Share the final notes",
            due_date=timezone.localdate() - timedelta(days=1),
        )
        resolved = Todo.objects.create(title="Archive old notes")
        resolved.resolve()

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<main class="page-shell">')
        self.assertContains(response, 'aria-labelledby="create-heading"')
        self.assertContains(response, f'data-todo-id="{active.pk}"')
        self.assertContains(response, 'status-badge--overdue')
        self.assertContains(response, 'status-badge--resolved')
        self.assertContains(response, f'href="{reverse("home")}?edit={active.pk}"')
        self.assertContains(response, f'action="{reverse("todo-resolve", args=[active.pk])}"')
        self.assertContains(response, f'action="{reverse("todo-reopen", args=[resolved.pk])}"')
        self.assertContains(response, f'href="{reverse("home")}?delete={active.pk}"')

    def test_invalid_create_associates_error_with_title_control(self):
        response = self.client.post(reverse("todo-create"), {"title": ""})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-describedby="id_title-error"')
        self.assertContains(response, 'id="id_title-error"')
        self.assertContains(response, 'role="alert"')

    def test_complete_htmx_journey_renders_fresh_server_fragments(self):
        create = self.client.post(
            reverse("todo-create"),
            {
                "title": "Ship release",
                "description": "Verify the checklist",
                "due_date": timezone.localdate().isoformat(),
            },
            **HTMX_HEADERS,
        )
        self.assertContains(create, "Ship release")
        todo = Todo.objects.get(title="Ship release")

        edit = self.client.post(
            reverse("todo-edit", args=[todo.pk]),
            {"title": "Ship release today", "description": "Done", "due_date": ""},
            **HTMX_HEADERS,
        )
        self.assertContains(edit, "Ship release today")

        resolve = self.client.post(reverse("todo-resolve", args=[todo.pk]), **HTMX_HEADERS)
        self.assertContains(resolve, "Resolved")
        reopen = self.client.post(reverse("todo-reopen", args=[todo.pk]), **HTMX_HEADERS)
        self.assertContains(reopen, "Active TODOs")

        confirm = self.client.get(
            reverse("todo-delete-confirm", args=[todo.pk]), **HTMX_HEADERS
        )
        self.assertContains(confirm, "Delete permanently")
        cancel = self.client.get(reverse("todo-delete-cancel", args=[todo.pk]), **HTMX_HEADERS)
        self.assertContains(cancel, "Ship release today")
        deleted = self.client.post(reverse("todo-delete", args=[todo.pk]), **HTMX_HEADERS)
        self.assertNotContains(deleted, "Ship release today")
        self.assertFalse(Todo.objects.filter(pk=todo.pk).exists())
