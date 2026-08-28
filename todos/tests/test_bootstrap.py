from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from config.database import database_config


class HomePageTests(TestCase):
    def test_home_page_uses_shared_application_shell(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "todos/home.html")
        self.assertContains(response, "TODO application")
        self.assertContains(response, "css/app.css")
        self.assertContains(response, "vendor/htmx/htmx.min.js")


class DatabaseConfigTests(SimpleTestCase):
    def test_sqlite_is_the_default(self):
        base_dir = Path("/project")

        config = database_config({}, base_dir)

        self.assertEqual(config["ENGINE"], "django.db.backends.sqlite3")
        self.assertEqual(config["NAME"], base_dir / "db.sqlite3")

    def test_postgresql_uses_explicit_environment_values(self):
        env = {
            "DB_ENGINE": "postgresql",
            "DB_NAME": "todo",
            "DB_USER": "todo_user",
            "DB_PASSWORD": "secret",
            "DB_HOST": "database.internal",
            "DB_PORT": "5432",
        }

        config = database_config(env, Path("/project"))

        self.assertEqual(
            config,
            {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": "todo",
                "USER": "todo_user",
                "PASSWORD": "secret",
                "HOST": "database.internal",
                "PORT": "5432",
            },
        )

    def test_postgresql_reports_missing_values(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "PostgreSQL configuration is missing: DB_USER, DB_PASSWORD, DB_HOST, DB_PORT",
        ):
            database_config(
                {"DB_ENGINE": "postgresql", "DB_NAME": "todo"},
                Path("/project"),
            )

    def test_unknown_database_engine_is_rejected(self):
        with self.assertRaisesMessage(
            ImproperlyConfigured,
            "DB_ENGINE must be either 'sqlite' or 'postgresql'.",
        ):
            database_config({"DB_ENGINE": "mysql"}, Path("/project"))
