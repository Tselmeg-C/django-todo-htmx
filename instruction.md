# AI-Native Development Workflow

Adapted from [AI-Native Development: Specifications, Loop and Graph Engineering](https://aishippingblog.com/p/ai-native-development-specifications).

Use this workflow to turn an idea into verified software while minimizing assumptions. Scale it to the task: use a direct prompt for small, clear changes; use the full role-based workflow only when the project or backlog justifies the extra time and cost.

## Core principles

1. Specify before coding. Do not implement a vague idea. Clarify the users, problem, workflow, behavior, edge cases, and boundaries first.
2. Make requirements observable. Write acceptance criteria that can be checked against the running result.
3. Keep context in the repository. Record durable commands, rules, decisions, and specialized guidance instead of relying on chat history.
4. Work on one small task at a time. Each task should fit in one focused session and contain enough context to stand alone.
5. Separate implementation from verification. The implementer writes the code; QA independently checks it against the specification.
6. Repeat against a measurable stop condition. Continue only while a concrete condition remains false, such as tests failing, QA returning `FAIL`, or open backlog items remaining.
7. Preserve traceability. Keep requirements, implementation notes, test evidence, QA findings, and follow-up work connected to the task.

## Phase 1: Clarify the product

Before choosing tools or writing code:

1. Start with the user's idea and identify every important ambiguity.
2. Ask focused questions, preferably one at a time, and offer options when the user may not know the alternatives.
3. Establish at least:
   - target users and their problem;
   - primary user journeys;
   - inputs, outputs, and visible behavior;
   - permissions, privacy, and failure behavior;
   - important edge cases;
   - MVP scope and explicit exclusions;
   - success criteria.
4. Summarize the agreed product in a Markdown specification such as `_docs/plan.md`.
5. Ask the user to review unresolved assumptions. Do not present guesses as decisions.

## Phase 2: Choose the technical approach

1. Read the approved product specification.
2. Propose a small number of suitable stack and architecture options without writing code.
3. Explain the tradeoffs that matter for this project, including maintainability, deployment, familiarity, and complexity.
4. Select an option with the user, or make a clearly stated recommendation when they delegate the choice.
5. Record the decision and its constraints in the repository.

## Phase 3: Build the backlog

1. Break the specification into ordered tasks.
2. Make every task small enough for one focused session and self-contained enough for a fresh implementer.
3. Make the first task an empty application skeleton with a passing test.
4. Merge trivial tasks, split oversized tasks, and remove non-MVP work.
5. Use the project's task tracker as the canonical backlog. Avoid maintaining a second active backlog in a Markdown file.

Use this task structure:

```markdown
## Goal

One or two sentences describing what will be true when the task is done.

## Acceptance criteria

- [ ] One observable, checkable behavior per line
- [ ] Include error paths and awkward cases

## Out of scope

- Excluded work, with links to follow-up tasks where appropriate

## Constraints

- Relevant files, libraries, architecture decisions, and project guidelines
```

## Phase 4: Create durable project context

Create a short `AGENTS.md` that tells an agent how to work in the repository. Include:

- setup, test, lint, build, and run commands;
- non-obvious project rules;
- dependency and architecture constraints;
- links to relevant documents under `_docs/`.

Keep detailed guidance in focused, living documents, for example:

- `_docs/process.md` for the development lifecycle;
- `_docs/testing-guidelines.md` for testing rules;
- `_docs/design-system.md` for UI consistency;
- `_docs/api.md` for interface decisions;
- `_docs/team/` for role definitions.

Link each document from `AGENTS.md` with a note saying when it should be read. Update these documents when user corrections reveal a durable rule. Keep them concise and do not load irrelevant context into every task.

## Phase 5: Groom one task

Act as the product manager before implementation:

1. Read the original task and linked product documents.
2. Rewrite it using the standard task structure.
3. Resolve ambiguity and add missed edge cases without inventing product decisions.
4. Make every acceptance criterion independently checkable.
5. Put excluded work in linked follow-up tasks; never silently discard it.
6. Do not write code while grooming.

Grooming is complete only when:

- all four task sections are present;
- every acceptance criterion has a clear pass/fail check;
- exclusions point to follow-up work when needed;
- a new implementer can complete the task using only the issue and linked documents.

Ask for user input if a missing product decision would materially change the result. Catching a misunderstanding here is cheaper than correcting completed code.

## Phase 6: Implement one groomed task

Act as the software engineer:

1. Read the complete task, acceptance criteria, constraints, and linked guidance.
2. Inspect the existing code and tests before changing anything.
3. Implement only the groomed scope. Do not rewrite or weaken acceptance criteria to fit the implementation.
4. Stay within the named constraints and preserve unrelated user changes.
5. Add tests for the new behavior and relevant edge cases.
6. Run focused checks during development, then the appropriate full suite.
7. Report what changed, what was tested, and any remaining concern.
8. Keep the task open for independent QA.

If a criterion is contradictory, impossible, or incompatible with repository constraints, stop that part of the implementation and report the conflict rather than silently changing the requirement.

Implementation is complete only when:

- every acceptance criterion is implemented;
- appropriate tests cover the new behavior;
- the relevant full test suite passes;
- the work and test evidence are recorded on the task.

## Phase 7: Verify independently

Act as QA after implementation. Judge the running behavior and code, not the implementer's claims.

1. Read the task's acceptance criteria.
2. Check every criterion against the actual result.
3. Run the relevant automated tests and record the exact commands and outcomes.
4. Test important acceptance cases that automation misses.
5. Do not fix defects during the QA pass; report them so the implementation and verification roles remain separate.
6. Produce exactly one overall verdict: `PASS` only if every criterion passes, otherwise `FAIL`.

Use this report shape:

```markdown
## QA: PASS | FAIL

- [x] Criterion — PASS
- [ ] Criterion — FAIL: action taken, expected result, and actual result

Tests: `<command>` — <result>
```

A QA report is complete only when every criterion has a verdict, every failure includes reproducible evidence, test commands and results are recorded, and QA has not modified the implementation.

## Phase 8: Run the correction loop

Use the QA verdict as the branch condition:

```text
groom task -> implement task -> QA
                              /  \
                          FAIL    PASS
                            |       |
                       implement   close task
                            |
                            +-----> QA
```

- On `FAIL`, return the QA evidence to the engineer, fix the defects, and run QA again.
- On `PASS`, close the task.
- Never close a task before QA passes.

## Phase 9: Work through a backlog

For an authorized multi-agent workflow, the main session acts as orchestrator and assigns the specialized roles. It should coordinate rather than perform the role work itself:

1. Pick the next open backlog item.
2. Send it through product grooming.
3. Send the groomed task to engineering.
4. Send the implementation to QA.
5. If QA returns `FAIL`, route its evidence back to engineering and repeat engineering → QA.
6. If QA returns `PASS`, close the task.
7. Continue until the backlog is empty or a genuine blocker requires user input.

Do not skip grooming, let engineering close its own task, let QA fix the code it judges, or let the orchestrator close a failed task.

## Loop and stop-condition rules

Before starting an autonomous loop, define a condition the agent can evaluate from evidence. Good examples include:

- every open issue has the required groomed sections;
- the specified test command exits successfully;
- QA reports `PASS` for the active task;
- no open backlog items remain.

Avoid subjective conditions such as “make it better.” At each iteration:

1. inspect current evidence;
2. perform the next bounded action;
3. run the required checks;
4. evaluate the stop condition;
5. continue if false, stop and report if true, or ask the user when genuinely blocked.

Use a goal/loop mechanism supplied by the agent harness when available. Do not use a multi-agent graph when a direct task or a single implementation loop is sufficient.

## Completion checklist

Before declaring work complete, confirm that:

- the delivered behavior matches an approved specification;
- every acceptance criterion is accounted for;
- scope exclusions and follow-ups are explicit;
- tests were run and their outcomes are reported;
- independent QA passed when the full role-based workflow was used;
- durable new lessons were added to the appropriate project document;
- the task tracker reflects the true final state.
