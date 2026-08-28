# Development Process

## Canonical work state

- GitHub Issues are the only active backlog.
- Process one open issue at a time, in dependency order unless the user changes priority.
- Read the entire issue and every linked document before acting.
- Keep scope changes, implementation evidence, QA findings, and follow-up work on the issue.
- Commit after meaningful, verified increments and push completed handoffs.

## Roles

- Product Manager — grooms one issue according to `_docs/team/pm.md`.
- Software Engineer — implements or fixes one groomed issue according to `_docs/team/software-engineer.md`.
- QA Engineer — independently checks an implementation according to `_docs/team/qa-engineer.md`.
- Orchestrator — coordinates handoffs and task state. Use separate agents only when the user authorizes a multi-agent workflow.

## Issue lifecycle

1. Select the next unblocked open issue.
2. Product Manager rewrites it with `_docs/task-template.md` and creates follow-up issues for moved scope.
3. The user reviews any material new product decision; otherwise the groomed criteria become the implementation contract.
4. Software Engineer implements only the groomed issue, adds tests, runs checks, commits the work, and comments with evidence.
5. QA Engineer independently checks every criterion and posts `PASS` or `FAIL` with test evidence. QA does not modify the implementation.
6. On `FAIL`, route the QA evidence back to engineering. Engineering fixes the issue, then QA starts a new verification pass.
7. On `PASS`, the orchestrator closes the issue.
8. Repeat until the backlog is empty.

## Handoff rules

- Do not skip grooming.
- The engineer does not change acceptance criteria or close the issue.
- QA ignores implementation claims and judges the criteria against actual behavior.
- QA reports defects without fixing them in the same pass.
- Only the orchestrator closes an issue, and only after QA reports `PASS`.
- If a criterion is contradictory or impossible, report the conflict instead of guessing.
- If work is moved out of scope, create and link a follow-up issue rather than silently dropping it.

## Stop conditions

Use observable stop conditions:

- grooming stops when every template section is complete and each criterion is checkable;
- implementation stops when all criteria are implemented, relevant tests exist, and the full suite passes;
- correction stops only when QA reports `PASS`;
- backlog processing stops when no open issues remain or a genuine blocker needs user input.
