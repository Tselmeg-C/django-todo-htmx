from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from todos.forms import TodoForm
from todos.models import Todo


class TodoFormTests(TestCase):
    def test_form_exposes_only_editable_fields_and_date_input(self):
        form = TodoForm()

        self.assertEqual(
            list(form.fields),
            ["title", "description", "due_date"],
        )
        self.assertFalse(form.fields["description"].required)
        self.assertFalse(form.fields["due_date"].required)
        self.assertEqual(form.fields["due_date"].widget.input_type, "date")

    def test_blank_title_is_rejected(self):
        for title in ("", "   "):
            with self.subTest(title=title):
                form = TodoForm(data={"title": title})

                self.assertFalse(form.is_valid())
                self.assertIn("title", form.errors)

        self.assertEqual(Todo.objects.count(), 0)

    def test_title_longer_than_200_characters_is_rejected(self):
        form = TodoForm(data={"title": "x" * 201})

        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_valid_title_is_trimmed_and_optional_fields_are_blank(self):
        form = TodoForm(data={"title": "  Plan release  "})

        self.assertTrue(form.is_valid(), form.errors)
        todo = form.save()

        self.assertEqual(todo.title, "Plan release")
        self.assertEqual(todo.description, "")
        self.assertIsNone(todo.due_date)

    def test_past_due_date_is_preserved(self):
        past_date = timezone.localdate() - timedelta(days=7)
        form = TodoForm(
            data={
                "title": "Record previous task",
                "description": "Historical work",
                "due_date": past_date.isoformat(),
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        todo = form.save()

        self.assertEqual(todo.due_date, past_date)
        self.assertEqual(todo.description, "Historical work")
