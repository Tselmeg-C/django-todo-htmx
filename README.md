# Django TODO

A small, server-rendered TODO application built with Django 5.2 and HTMX. It supports the complete MVP workflow: create, edit, resolve, reopen, and permanently delete TODOs with optional descriptions and due dates.

## Features

- Active and resolved TODO sections
- Due dates, overdue cues, and urgency-based ordering
- Inline create and edit forms with HTMX enhancement
- Resolve/reopen actions
- Confirmation before permanent deletion
- Responsive, keyboard-friendly HTML and project-owned CSS
- SQLite by default, with PostgreSQL configuration support

## Requirements

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/)

## Quick start

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

Open <http://localhost:8000/>.

## Configuration

The default database is the repository-local `db.sqlite3`. To use PostgreSQL, set `DB_ENGINE=postgresql` and provide the values documented in `.env.example`:

```bash
export DB_ENGINE=postgresql
export DB_NAME=django_todo
export DB_USER=django_todo
export DB_PASSWORD=replace-me
export DB_HOST=localhost
export DB_PORT=5432
```

For deployment, also set a unique `DJANGO_SECRET_KEY`, disable debug, and configure `DJANGO_ALLOWED_HOSTS`.

## Development commands

```bash
# Run the full test suite
uv run python manage.py test

# Run Django checks
uv run python manage.py check

# Confirm there are no uncommitted model migrations
uv run python manage.py makemigrations --check --dry-run

# Validate the dependency lockfile
uv lock --check
```

## Architecture

The application uses Django function-based views, Django templates, and the built-in test framework. HTMX is vendored under `static/vendor/htmx/` and progressively enhances normal HTML links and forms; the server remains the source of truth and returns reusable HTML fragments. No frontend build tool, CSS framework, JSON API, or authentication layer is required for this MVP.

Project guidance and durable decisions live in `_docs/plan.md`, `_docs/architecture.md`, and `_docs/testing-guidelines.md`.
