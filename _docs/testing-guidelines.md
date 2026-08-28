# Testing Guidelines

## Test strategy

- Use Django's built-in `TestCase`, test client, and form/model testing utilities.
- Test public behavior and durable domain rules; avoid assertions tied to incidental HTML formatting or private implementation details.
- Add a regression test before or with every defect fix.
- Keep tests deterministic. Control dates and timestamps rather than relying on the wall clock where boundaries matter.
- Use factories or helpers only when they reduce meaningful repetition without hiding the scenario.

## Required coverage by layer

- Models: field behavior, resolve/reopen invariant, overdue calculation, and ordering helpers.
- Forms: required and optional values, title length, past dates, and invalid data preservation.
- Views: status codes, templates/fragments, redirects, POST-only mutations, missing objects, and stored results.
- Templates: empty states, active/resolved state, due dates, overdue text cues, validation errors, and controls.
- Integration: primary create/edit/resolve/reopen/delete journeys and HTMX versus non-HTMX behavior.

## Execution

During implementation, run the narrowest relevant test module first. Before engineering handoff and again during QA, run:

```text
uv run python manage.py test
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
```

Record the exact commands and results on the GitHub issue. A passing suite does not override a failed acceptance criterion.
