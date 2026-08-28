from datetime import timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from todos.models import Todo

HTMX_HEADERS = {"HTTP_HX_REQUEST": "true"}


class TodoActionViewTests(TestCase):
    def test_cards_show_only_the_status_action_that_applies(self):
        active = Todo.objects.create(title="Active action")
        resolved = Todo.objects.create(title="Resolved action")
        resolved.resolve()

        response = self.client.get(reverse("home"))

        self.assertContains(
            response,
            f'action="{reverse("todo-resolve", args=[active.pk])}"',
        )
        self.assertNotContains(
            response,
            f'action="{reverse("todo-reopen", args=[active.pk])}"',
        )
        self.assertContains(
            response,
            f'action="{reverse("todo-reopen", args=[resolved.pk])}"',
        )
        self.assertNotContains(
            response,
            f'action="{reverse("todo-resolve", args=[resolved.pk])}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("home")}?delete={active.pk}"',
        )
        self.assertContains(
            response,
            f'href="{reverse("home")}?delete={resolved.pk}"',
        )

    def test_non_htmx_resolve_redirects_and_moves_todo(self):
        todo = Todo.objects.create(
            title="Resolve me",
            due_date=timezone.localdate() - timedelta(days=1),
        )

        response = self.client.post(reverse("todo-resolve", args=[todo.pk]))

        self.assertRedirects(response, reverse("home"))
        todo.refresh_from_db()
        self.assertTrue(todo.is_resolved)
        self.assertIsNotNone(todo.resolved_at)
        home = self.client.get(reverse("home"))
        self.assertNotContains(home, "Overdue")
        self.assertContains(home, "Resolved")

    def test_htmx_resolve_returns_fresh_sections_without_overdue_cue(self):
        todo = Todo.objects.create(
            title="Resolve with HTMX",
            due_date=timezone.localdate() - timedelta(days=1),
        )

        response = self.client.post(
            reverse("todo-resolve", args=[todo.pk]),
            **HTMX_HEADERS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"].split(";")[0], "text/html")
        self.assertTemplateUsed(response, "todos/partials/todo_sections.html")
        self.assertTemplateNotUsed(response, "base.html")
        self.assertQuerySetEqual(response.context["active_todos"], [])
        self.assertQuerySetEqual(response.context["resolved_todos"], [todo])
        self.assertContains(response, "Resolved")
        self.assertNotContains(response, "Overdue")

    def test_reopen_moves_todo_back_to_active(self):
        todo = Todo.objects.create(
            title="Reopen me",
            due_date=timezone.localdate() + timedelta(days=2),
        )
        todo.resolve()

        response = self.client.post(
            reverse("todo-reopen", args=[todo.pk]),
            **HTMX_HEADERS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todos/partials/todo_sections.html")
        todo.refresh_from_db()
        self.assertFalse(todo.is_resolved)
        self.assertIsNone(todo.resolved_at)
        self.assertQuerySetEqual(response.context["active_todos"], [todo])
        self.assertQuerySetEqual(response.context["resolved_todos"], [])

    def test_repeated_transition_posts_are_idempotent(self):
        todo = Todo.objects.create(title="Repeat transition")
        todo.resolve()
        todo.refresh_from_db()
        first_resolution = todo.resolved_at
        first_update = todo.updated_at

        self.client.post(reverse("todo-resolve", args=[todo.pk]))
        todo.refresh_from_db()
        self.assertEqual(todo.resolved_at, first_resolution)
        self.assertEqual(todo.updated_at, first_update)

        todo.reopen()
        todo.refresh_from_db()
        reopened_update = todo.updated_at
        self.client.post(reverse("todo-reopen", args=[todo.pk]))
        todo.refresh_from_db()
        self.assertIsNone(todo.resolved_at)
        self.assertEqual(todo.updated_at, reopened_update)

    def test_delete_confirmation_is_visible_and_non_destructive(self):
        todo = Todo.objects.create(title="Delete carefully")

        response = self.client.get(
            reverse("todo-delete-confirm", args=[todo.pk]),
            **HTMX_HEADERS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "todos/partials/todo_delete_confirm.html",
        )
        self.assertContains(response, "Delete carefully")
        self.assertContains(response, "permanently")
        self.assertContains(response, "cannot be undone")
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertTrue(Todo.objects.filter(pk=todo.pk).exists())

        fallback = self.client.get(reverse("todo-delete-confirm", args=[todo.pk]))
        self.assertRedirects(
            fallback,
            f"{reverse('home')}?delete={todo.pk}",
        )
        fallback_page = self.client.get(fallback.url)
        self.assertContains(fallback_page, "Delete carefully")
        self.assertContains(fallback_page, "Delete permanently")
        self.assertTrue(Todo.objects.filter(pk=todo.pk).exists())

    def test_delete_cancel_restores_card_without_mutation(self):
        todo = Todo.objects.create(title="Keep this one")
        confirm = self.client.get(
            reverse("todo-delete-confirm", args=[todo.pk]),
            **HTMX_HEADERS,
        )
        self.assertContains(
            confirm,
            f'hx-get="{reverse("todo-delete-cancel", args=[todo.pk])}"',
        )

        response = self.client.get(
            reverse("todo-delete-cancel", args=[todo.pk]),
            **HTMX_HEADERS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Delete permanently")
        self.assertContains(response, "Keep this one")
        self.assertTrue(Todo.objects.filter(pk=todo.pk).exists())

        fallback = self.client.get(reverse("todo-delete-cancel", args=[todo.pk]))
        self.assertRedirects(fallback, reverse("home"))

    def test_confirmed_delete_removes_only_the_selected_todo(self):
        active = Todo.objects.create(title="Delete active")
        resolved = Todo.objects.create(title="Keep resolved")
        resolved.resolve()

        response = self.client.post(
            reverse("todo-delete", args=[active.pk]),
            **HTMX_HEADERS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todos/partials/todo_sections.html")
        self.assertFalse(Todo.objects.filter(pk=active.pk).exists())
        self.assertTrue(Todo.objects.filter(pk=resolved.pk).exists())
        self.assertContains(response, "Keep resolved")

        fallback = self.client.post(reverse("todo-delete", args=[resolved.pk]))
        self.assertRedirects(fallback, reverse("home"))
        self.assertFalse(Todo.objects.filter(pk=resolved.pk).exists())

    def test_action_methods_missing_ids_and_malformed_queries_are_controlled(self):
        todo = Todo.objects.create(title="Method target")
        post_only = ("todo-resolve", "todo-reopen", "todo-delete")
        for name in post_only:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.get(reverse(name, args=[todo.pk])).status_code,
                    405,
                )

        get_only = ("todo-delete-confirm", "todo-delete-cancel")
        for name in get_only:
            with self.subTest(name=name):
                self.assertEqual(
                    self.client.post(reverse(name, args=[todo.pk])).status_code,
                    405,
                )

        for name, method in (
            ("todo-resolve", "post"),
            ("todo-reopen", "post"),
            ("todo-delete-confirm", "get"),
            ("todo-delete-cancel", "get"),
            ("todo-delete", "post"),
        ):
            with self.subTest(name=name):
                response = getattr(self.client, method)(
                    reverse(name, args=[999999])
                )
                self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.client.get(f"{reverse('home')}?delete=invalid").status_code,
            404,
        )

    def test_action_posts_require_csrf_and_token_bearing_resolve_succeeds(self):
        todo = Todo.objects.create(title="CSRF action")
        csrf_client = Client(enforce_csrf_checks=True)

        for name in ("todo-resolve", "todo-delete"):
            with self.subTest(name=name):
                self.assertEqual(
                    csrf_client.post(reverse(name, args=[todo.pk])).status_code,
                    403,
                )

        csrf_client.get(reverse("home"))
        token = csrf_client.cookies["csrftoken"].value
        response = csrf_client.post(
            reverse("todo-resolve", args=[todo.pk]),
            {"csrfmiddlewaretoken": token},
        )

        self.assertRedirects(response, reverse("home"))
        todo.refresh_from_db()
        self.assertTrue(todo.is_resolved)
