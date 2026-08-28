# TODO Application Product Specification

Status: Approved by the user on 2026-08-28.

## Product goal

Build a small, single-user web application for recording and managing personal TODOs. The first release should make deadlines and unfinished work easy to see without adding collaboration or productivity features beyond the requested scope.

## Target user and access

- The application has one shared TODO list.
- There are no user accounts, authentication, or authorization rules.
- Anyone with access to the running application can view and modify the same TODOs.

## TODO data

Each TODO contains:

- a required title;
- an optional description;
- an optional calendar due date;
- a status: active or resolved;
- creation and update timestamps;
- a resolution timestamp when resolved.

The title must not be blank. Invalid form submissions must show a clear validation message and must not create or alter a TODO.

## Main interface

The application uses one main page with two sections:

1. **Active TODOs**
2. **Resolved TODOs**

Creation and editing happen inline on this page rather than on dedicated pages or in modal dialogs. The interface must remain understandable and usable on desktop and mobile screens.

When no TODOs exist in a section, that section displays an appropriate empty-state message.

## Create a TODO

- The main page provides an inline creation form.
- A user can enter a title, optional description, and optional due date.
- Saving valid input adds the TODO to the active section.
- A due date in the past is valid and causes the new TODO to appear as overdue immediately.
- Cancelling or abandoning input does not create a TODO.

## Edit a TODO

- A user can open an inline edit form for an existing active or resolved TODO.
- The title, description, and due date can be changed.
- Saving valid input updates the existing TODO without changing its identity or status.
- Cancelling editing preserves the previously saved values.
- Invalid input leaves the saved TODO unchanged and displays a clear validation message.

## Delete a TODO

- A user can request deletion of an active or resolved TODO.
- The interface asks for confirmation before deletion.
- Confirming permanently deletes the TODO.
- Cancelling confirmation leaves it unchanged.
- A trash or restore feature is not included.

## Resolve and reopen a TODO

- A user can mark an active TODO as resolved.
- Resolving records the resolution time and moves the TODO to the resolved section.
- A user can reopen a resolved TODO.
- Reopening clears its resolution time and returns it to the active section.
- Resolved TODOs are never styled or labeled as overdue, even when their due dates are in the past.

## Due dates and ordering

- Due dates are calendar dates without a time of day.
- An active TODO is overdue when its due date is earlier than the current calendar date.
- Overdue TODOs have a clear visible label or style that does not depend on color alone.
- Due dates in the past are allowed during creation and editing.

Active TODOs are ordered as follows:

1. overdue TODOs, oldest due date first;
2. non-overdue TODOs with due dates, nearest due date first;
3. TODOs without due dates;
4. ties are resolved with the most recently created TODO first.

Resolved TODOs are ordered by resolution time, most recently resolved first.

## Feedback and failure behavior

- Forms display field-specific validation errors where practical.
- User actions must not silently fail.
- Attempts to act on a TODO that no longer exists return a normal not-found response rather than a server error.
- The interface uses clear text labels for actions and status.
- Destructive actions are visually distinguishable and require confirmation.

## Presentation requirements

- The interface is clean and responsive on desktop and mobile.
- Active and resolved sections are visually distinct.
- Forms, validation errors, due dates, overdue state, and action controls are easy to identify.
- Core actions can be completed using a keyboard.
- Overdue state and validation must not be communicated by color alone.

## Primary user journeys

1. Open the home page and see active and resolved TODOs.
2. Create a TODO with only a title.
3. Create a TODO with a description and due date.
4. Correct an invalid form submission.
5. Edit or cancel editing an existing TODO inline.
6. Resolve an active TODO and see it move to the resolved section.
7. Reopen a resolved TODO and see it return to the active section.
8. Request deletion, then either cancel or confirm it.
9. Recognize overdue active TODOs and see the list ordered by urgency.

## MVP exclusions

The first release does not include:

- user accounts or private lists;
- multiple lists or team collaboration;
- priorities, tags, categories, or manual ordering;
- search or filters;
- reminders or notifications;
- recurring TODOs;
- file attachments or comments;
- bulk actions;
- a public API;
- soft deletion, trash, or restore;
- date-and-time deadlines;
- animations or advanced frontend interactions.

## Success criteria

The MVP is successful when:

- every primary user journey works through the rendered web interface;
- create, edit, delete, resolve, and reopen behavior is covered by automated tests;
- optional and past due dates behave as specified;
- active and resolved ordering is covered by automated tests;
- validation and not-found cases return controlled, understandable responses;
- the full automated test suite passes;
- the interface is usable at common mobile and desktop widths;
- independent QA verifies every groomed acceptance criterion before the corresponding task is closed.

## Assumptions requiring review

- A title has a practical maximum length chosen during technical design; the description may be multi-line.
- “Current calendar date” uses the Django application's configured local date. Because deadlines have no time component, the application does not display a timezone.
- Inline editing means one TODO can enter edit mode within the list; saving or cancelling returns it to display mode.
- Permanent deletion uses a browser-visible confirmation step; its exact implementation will be chosen during technical design.

These assumptions were approved with the rest of the specification. Technical decisions are recorded in [`architecture.md`](architecture.md).
