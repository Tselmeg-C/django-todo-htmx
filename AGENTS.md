# Repository Instructions

## Commands

- `uv sync` — install locked project dependencies.
- `uv run python manage.py test` — run the complete automated test suite.
- `uv run python manage.py runserver` — run the local development server.
- `uv run python manage.py check` — run Django system checks.
- `uv run python manage.py makemigrations --check --dry-run` — verify that model changes have committed migrations.

Some commands become available after bootstrap issue #1 is implemented.

## Rules

- Follow the approved product behavior in `_docs/plan.md`.
- Follow technical decisions and constraints in `_docs/architecture.md`.
- Follow the task lifecycle in `_docs/process.md`.
- GitHub Issues are the only active backlog. Work on one issue at a time.
- Groom an issue before implementing it. Use `_docs/task-template.md`.
- Do not weaken or silently reinterpret acceptance criteria during implementation.
- Preserve unrelated user changes.
- Add Python dependencies only in `pyproject.toml`, explain why they are needed, and update the lockfile.
- Use Django migrations for schema changes.
- Run relevant focused tests during development and the full suite before handoff.
- Do not close an issue until independent QA reports `PASS` against every acceptance criterion.

## Documents

- `_docs/plan.md` — read for product behavior, user journeys, and MVP boundaries.
- `_docs/architecture.md` — read before technical design or implementation.
- `_docs/process.md` — read before starting, handing off, or closing an issue.
- `_docs/task-template.md` — use when grooming a GitHub issue.
- `_docs/testing-guidelines.md` — read before writing or reviewing tests.
- `_docs/team/pm.md` — follow when grooming an issue.
- `_docs/team/software-engineer.md` — follow when implementing or fixing an issue.
- `_docs/team/qa-engineer.md` — follow during independent verification.
