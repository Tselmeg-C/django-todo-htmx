"""Database configuration derived from explicit environment variables."""

from pathlib import Path
from typing import Mapping

from django.core.exceptions import ImproperlyConfigured

POSTGRES_VARIABLES = (
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
    "DB_HOST",
    "DB_PORT",
)


def database_config(env: Mapping[str, str], base_dir: Path) -> dict[str, str]:
    """Return a Django database configuration for SQLite or PostgreSQL."""
    engine = env.get("DB_ENGINE", "sqlite").strip().lower()

    if engine == "sqlite":
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": base_dir / "db.sqlite3",
        }

    if engine == "postgresql":
        missing = [name for name in POSTGRES_VARIABLES if not env.get(name)]
        if missing:
            missing_names = ", ".join(missing)
            raise ImproperlyConfigured(
                f"PostgreSQL configuration is missing: {missing_names}"
            )

        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": env["DB_NAME"],
            "USER": env["DB_USER"],
            "PASSWORD": env["DB_PASSWORD"],
            "HOST": env["DB_HOST"],
            "PORT": env["DB_PORT"],
        }

    raise ImproperlyConfigured(
        "DB_ENGINE must be either 'sqlite' or 'postgresql'."
    )
