from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.test import SimpleTestCase

from todos.admin import TodoAdmin
from todos.models import Todo


class TodoAdminTests(SimpleTestCase):
    def test_todo_is_registered_with_identifying_list_columns(self):
        self.assertTrue(admin.site.is_registered(Todo))

        model_admin = TodoAdmin(Todo, AdminSite())
        self.assertEqual(
            model_admin.list_display,
            ("title", "due_date", "is_resolved"),
        )
