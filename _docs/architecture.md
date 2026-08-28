# TODO Application Architecture

Status: Approved through step-by-step user decisions on 2026-08-28.

## Summary

Build a server-rendered Django application with HTMX-enhanced inline interactions. Django remains responsible for routing, validation, persistence, HTML rendering, and security controls. HTMX submits requests and swaps server-rendered HTML fragments; the project does not expose a JSON API or introduce a client-side application framework.

## Runtime and dependencies

- Python 3.12 or another version supported by the selected Django release.
- Django 5.2 LTS, constrained to compatible patch releases with `>=5.2,<5.3`.
- HTMX 2.0.10, stored as a pinned project static asset rather than loaded from a CDN.
- PostgreSQL support through the `psycopg` driver.
- No CSS framework, JavaScript framework, or frontend build tool.

Python dependencies are declared in `pyproject.toml`, resolved and locked with `uv`, and installed with `uv sync`.

## Project structure

- A small Django project package owns global configuration and root URLs.
- One Django app owns TODO models, forms, views, routes, templates, static styles, and tests.
- Shared page templates are separated from reusable TODO fragments returned to HTMX requests.
- Project documentation lives under `_docs/` and is linked from `AGENTS.md`.

Prefer explicit function-based views for this small application. Keep business rules in the model or focused domain functions when they are reused; do not hide application behavior in templates or JavaScript.

## Rendering and interactions

- The initial request renders the complete home page.
- Create, edit, resolve, reopen, and delete requests use normal Django routes and server-side forms.
- HTMX requests receive HTML fragments suitable for swapping into the page.
- Important endpoints retain a valid non-HTMX response or redirect where practical, so core actions do not depend on JavaScript for correctness.
- The server is always the source of truth after a mutation. Client code must not invent or independently reconcile TODO state.
- Use POST for state-changing operations and include Django CSRF protection.
- Deletion requires an explicit browser-visible confirmation before its POST request.

The vendored HTMX file must retain its upstream license and version provenance. No npm installation or runtime CDN connection is required.

## Data model

Use one TODO model with:

- `title`: required text with a 200-character maximum;
- `description`: optional multi-line text;
- `due_date`: optional calendar date;
- `is_resolved`: boolean status;
- `created_at`: automatically recorded creation timestamp;
- `updated_at`: automatically recorded update timestamp;
- `resolved_at`: nullable resolution timestamp.

Model behavior must preserve the invariant that active TODOs have no resolution timestamp and resolved TODOs have one. Resolve and reopen operations update both fields together.

Overdue state is derived rather than stored: a TODO is overdue when it is active, has a due date, and that due date is earlier than Django's configured local date.

## Database configuration

- SQLite is the zero-configuration local default.
- PostgreSQL is selected when the required `DB_*` environment variables are present.
- Read PostgreSQL connection values from standard project-specific variables for engine selection, database name, user, password, host, and port.
- Do not require a `DATABASE_URL` parser or separate settings module.
- Keep credentials out of source control and provide a safe example environment file if configuration needs documentation.

Schema changes are managed exclusively through Django migrations and committed with the corresponding model changes.

## Ordering

Ordering rules are implemented in server-side query logic and covered by tests.

Active TODOs:

1. overdue items, oldest due date first;
2. current or future dated items, nearest due date first;
3. undated items;
4. ties, newest creation first.

Resolved TODOs are ordered by resolution timestamp, newest first.

Database-neutral Django expressions must be used so ordering behaves consistently on SQLite and PostgreSQL.

## Forms and validation

- Use Django `ModelForm` validation for title, description, and due date.
- Title is required, trimmed according to Django's normal form behavior, and limited to 200 characters.
- Description and due date are optional.
- Past due dates are accepted.
- Invalid create or edit submissions return the relevant bound form and errors without mutating stored data.
- Attempts to mutate a missing TODO return HTTP 404.

## Styling and accessibility

- Use project-owned semantic HTML and CSS.
- Use responsive layout rules without a CSS framework.
- Provide visible keyboard focus states and text labels for controls.
- Do not communicate overdue or error state through color alone.
- Keep native form controls and semantic buttons unless a custom interaction has a demonstrated need.

## Testing

Use Django's built-in test framework and test client through:

```text
uv run python manage.py test
```

Tests cover:

- model invariants and overdue calculation;
- forms and validation;
- create, edit, delete, resolve, and reopen endpoints;
- HTMX fragment responses and important non-HTMX fallbacks;
- active and resolved ordering;
- CSRF-compatible POST-only mutations and missing-object behavior;
- rendered empty, validation, due-date, overdue, active, and resolved states.

Browser automation is out of scope for the MVP. Independent QA must still inspect the rendered user journeys at desktop and mobile widths.

## Constraints and exclusions

- Follow [`plan.md`](plan.md) for product behavior and MVP boundaries.
- Do not add Django REST Framework, a public API, authentication, task queues, notification services, or frontend build tooling.
- Do not add a dependency without recording why it is necessary.
- Prefer the simplest server-rendered implementation that meets the accepted behavior.
