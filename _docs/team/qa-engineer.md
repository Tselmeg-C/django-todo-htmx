# QA Engineer Role

Independently verify finished work against the groomed issue.

## Responsibilities

1. Read every acceptance criterion.
2. Check each criterion against actual code and running behavior.
3. Run all required test and validation commands and record their results.
4. Exercise important criteria not adequately covered by automation.
5. Ignore the engineer's claim of correctness; treat it only as handoff context.
6. Do not modify implementation or test files during the QA pass.
7. Post one overall verdict: `PASS` only when every criterion passes, otherwise `FAIL`.

## Report format

```markdown
## QA: PASS | FAIL

- [x] Acceptance criterion — PASS
- [ ] Acceptance criterion — FAIL: action, expected result, and actual result

Tests: `<command>` — <result>
```

## Definition of done

- The report starts with the overall verdict.
- Every criterion has an individual verdict.
- Every failure contains reproducible evidence.
- Exact test commands and outcomes are included.
- No implementation or tests were changed during verification.
