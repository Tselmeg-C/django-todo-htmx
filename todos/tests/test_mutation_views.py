from datetime import timedelta

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from todos.models import Todo

HTMX_HEADERS = {"HTTP_HX_REQUEST": "true"}


class TodoMutationViewTests(TestCase):
    def test_home_renders_labeled_csrf_protected_create_form(self):
        response = self.client.get(reverse("home"))

        self.assertTemplateUsed(response, "todos/partials/todo_app.html")
        self.assertTemplateUsed(response, "todos/partials/todo_form.html")
        self.assertContains(response, 'id="todo-create-form"')
        self.assertContains(response, "Title")
        self.assertContains(response, "Description")
        self.assertContains(response, "Due date")
        self.assertContains(response, 'name="csrfmiddlewaretoken"')
        self.assertContains(
            response,
            '<button class="button button--primary" type="submit">Add TODO</button>',
            html=True,
        )

    def test_non_htmx_create_stores_valid_values_and_redirects(self):
        past_date = timezone.localdate() - timedelta(days=3)

        response = self.client.post(
            reverse("todo-create"),
            {
                "title": "  Record completed preparation  ",
                "description": "Keep the history",
                "due_date": past_date.isoformat(),
            },
        )

        self.assertRedirects(response, reverse("home"))
        todo = Todo.objects.get()
        self.assertEqual(todo.title, "Record completed preparation")
        self.assertEqual(todo.description, "Keep the history")
        self.assertEqual(todo.due_date, past_date)
        self.assertFalse(todo.is_resolved)
        self.assertIsNone(todo.resolved_at)

    def test_htmx_create_returns_reset_app_fragment_in_current_order(self):
        later = Todo.objects.create(
            title="Later task",
            due_date=timezone.localdate() + timedelta(days=3),
        )

        response = self.client.post(
            reverse("todo-create"),
            {
                "title": "Due today",
                "due_date": timezone.localdate().isoformat(),
            },
            **HTMX_HEADERS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"].split(";")[0], "text/html")
        self.assertTemplateUsed(response, "todos/partials/todo_app.html")
        self.assertTemplateNotUsed(response, "base.html")
        self.assertContains(response, 'id="todo-app"')
        self.assertFalse(response.context["create_form"].is_bound)
        created = Todo.objects.get(title="Due today")
        self.assertQuerySetEqual(response.context["active_todos"], [created, later])
        content = response.content.decode()
        self.assertLess(content.index(created.title), content.index(later.title))
        self.assertIn("HX-Request", response.get("Vary", ""))

    def test_invalid_create_preserves_bound_values_without_storing(self):
        submitted = {
            "title": "   ",
            "description": "Keep this input",
            "due_date": timezone.localdate().isoformat(),
        }

        for headers, expected_template in (
            (HTMX_HEADERS, "todos/partials/todo_app.html"),
            ({}, "todos/home.html"),
        ):
            with self.subTest(headers=headers):
                response = self.client.post(
                    reverse("todo-create"),
                    submitted,
                    **headers,
                )

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, expected_template)
                form = response.context["create_form"]
                self.assertTrue(form.is_bound)
                self.assertIn("title", form.errors)
                self.assertEqual(form.data["title"], "   ")
                self.assertEqual(form.data["description"], "Keep this input")
                self.assertContains(response, "Keep this input")
                self.assertContains(response, 'class="form-error"')
                self.assertEqual(Todo.objects.count(), 0)

    def test_edit_controls_and_htmx_form_allow_only_one_active_editor(self):
        first = Todo.objects.create(
            title="First task",
            description="First description",
        )
        second = Todo.objects.create(title="Second task")
        home_response = self.client.get(reverse("home"))

        self.assertContains(
            home_response,
            f'href="{reverse("home")}?edit={first.pk}"',
        )
        self.assertContains(
            home_response,
            f'hx-get="{reverse("todo-edit", args=[first.pk])}"',
        )

        for todo in (first, second):
            with self.subTest(todo=todo):
                response = self.client.get(
                    reverse("todo-edit", args=[todo.pk]),
                    **HTMX_HEADERS,
                )

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, "todos/partials/todo_sections.html")
                self.assertTemplateUsed(response, "todos/partials/todo_form.html")
                self.assertContains(response, f'id="todo-edit-form-{todo.pk}"')
                self.assertEqual(
                    response.content.count(b'id="todo-edit-form-'),
                    1,
                )
                self.assertEqual(response.context["edit_form"].instance, todo)
                self.assertContains(response, f'value="{todo.title}"')

    def test_non_htmx_edit_get_redirects_to_usable_inline_page(self):
        todo = Todo.objects.create(title="Edit through fallback")

        response = self.client.get(reverse("todo-edit", args=[todo.pk]))

        self.assertRedirects(response, f"{reverse('home')}?edit={todo.pk}")
        fallback = self.client.get(response.url)
        self.assertContains(fallback, f'id="todo-edit-form-{todo.pk}"')
        self.assertContains(fallback, todo.title)

    def test_valid_edit_preserves_identity_and_resolved_state(self):
        todo = Todo.objects.create(title="Original", due_date=timezone.localdate())
        todo.resolve()
        original_pk = todo.pk
        original_resolution = todo.resolved_at
        new_date = timezone.localdate() + timedelta(days=7)

        response = self.client.post(
            reverse("todo-edit", args=[todo.pk]),
            {
                "title": "Updated",
                "description": "Updated description",
                "due_date": new_date.isoformat(),
                "is_resolved": "",
            },
        )

        self.assertRedirects(response, reverse("home"))
        todo.refresh_from_db()
        self.assertEqual(todo.pk, original_pk)
        self.assertEqual(todo.title, "Updated")
        self.assertEqual(todo.description, "Updated description")
        self.assertEqual(todo.due_date, new_date)
        self.assertTrue(todo.is_resolved)
        self.assertEqual(todo.resolved_at, original_resolution)

    def test_valid_htmx_edit_reorders_fresh_server_rendered_sections(self):
        first = Todo.objects.create(
            title="First",
            due_date=timezone.localdate() + timedelta(days=2),
        )
        moved = Todo.objects.create(
            title="Move earlier",
            due_date=timezone.localdate() + timedelta(days=5),
        )

        response = self.client.post(
            reverse("todo-edit", args=[moved.pk]),
            {
                "title": moved.title,
                "description": "",
                "due_date": timezone.localdate().isoformat(),
            },
            **HTMX_HEADERS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todos/partials/todo_sections.html")
        self.assertTemplateNotUsed(response, "base.html")
        self.assertNotContains(response, "todo-edit-form-")
        self.assertQuerySetEqual(response.context["active_todos"], [moved, first])
        content = response.content.decode()
        self.assertLess(content.index(moved.title), content.index(first.title))

    def test_cancel_restores_card_without_changing_saved_values(self):
        todo = Todo.objects.create(
            title="Saved title",
            description="Saved description",
        )
        edit_response = self.client.get(
            reverse("todo-edit", args=[todo.pk]),
            **HTMX_HEADERS,
        )
        self.assertContains(edit_response, f'href="{reverse("home")}"')
        self.assertContains(
            edit_response,
            f'hx-get="{reverse("todo-edit-cancel", args=[todo.pk])}"',
        )

        response = self.client.get(
            reverse("todo-edit-cancel", args=[todo.pk]),
            **HTMX_HEADERS,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "todos/partials/todo_sections.html")
        self.assertNotContains(response, "todo-edit-form-")
        self.assertContains(response, "Saved title")
        todo.refresh_from_db()
        self.assertEqual(todo.title, "Saved title")
        self.assertEqual(todo.description, "Saved description")

    def test_invalid_edit_preserves_database_and_bound_submitted_values(self):
        todo = Todo.objects.create(
            title="Stored title",
            description="Stored description",
        )
        submitted = {
            "title": "",
            "description": "Submitted description",
            "due_date": "",
        }

        for headers, expected_template in (
            (HTMX_HEADERS, "todos/partials/todo_sections.html"),
            ({}, "todos/home.html"),
        ):
            with self.subTest(headers=headers):
                response = self.client.post(
                    reverse("todo-edit", args=[todo.pk]),
                    submitted,
                    **headers,
                )

                self.assertEqual(response.status_code, 200)
                self.assertTemplateUsed(response, expected_template)
                form = response.context["edit_form"]
                self.assertTrue(form.is_bound)
                self.assertIn("title", form.errors)
                self.assertEqual(form.data["title"], "")
                self.assertEqual(
                    form.data["description"],
                    "Submitted description",
                )
                self.assertContains(response, "Submitted description")
                self.assertContains(response, f'id="todo-edit-form-{todo.pk}"')
                todo.refresh_from_db()
                self.assertEqual(todo.title, "Stored title")
                self.assertEqual(todo.description, "Stored description")

    def test_methods_and_missing_todos_return_controlled_responses(self):
        todo = Todo.objects.create(title="Existing")

        self.assertEqual(self.client.get(reverse("todo-create")).status_code, 405)
        self.assertEqual(
            self.client.put(reverse("todo-edit", args=[todo.pk])).status_code,
            405,
        )
        self.assertEqual(
            self.client.post(
                reverse("todo-edit-cancel", args=[todo.pk])
            ).status_code,
            405,
        )
        self.assertEqual(
            self.client.get(reverse("todo-edit", args=[999999])).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(reverse("todo-edit", args=[999999]), {}).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(
                reverse("todo-edit-cancel", args=[999999])
            ).status_code,
            404,
        )
        self.assertEqual(self.client.get(f"{reverse('home')}?edit=bad").status_code, 404)
        self.assertEqual(
            self.client.get(f"{reverse('home')}?edit=999999").status_code,
            404,
        )

    def test_create_and_edit_posts_require_csrf_tokens(self):
        todo = Todo.objects.create(title="Protected")
        csrf_client = Client(enforce_csrf_checks=True)

        self.assertEqual(
            csrf_client.post(reverse("todo-create"), {"title": "Blocked"}).status_code,
            403,
        )
        self.assertEqual(
            csrf_client.post(
                reverse("todo-edit", args=[todo.pk]),
                {"title": "Blocked edit"},
            ).status_code,
            403,
        )

        csrf_client.get(reverse("home"))
        token = csrf_client.cookies["csrftoken"].value
        response = csrf_client.post(
            reverse("todo-create"),
            {
                "title": "Allowed",
                "csrfmiddlewaretoken": token,
            },
        )
        self.assertRedirects(response, reverse("home"))
        self.assertTrue(Todo.objects.filter(title="Allowed").exists())
