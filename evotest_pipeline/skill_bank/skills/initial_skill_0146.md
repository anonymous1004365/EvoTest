---
name: du-command-pattern-filtering
description: When testing a shell command that accepts both file names and regex patterns,
  test that patterns correctly filter results by matching against all positional arguments,
  and that patterns with wildcards like '.*' do not match partial strings unexpectedly.
code_tags:
- VALIDATION
- STATE_MUTATION
- REGEX_PATTERN_IN_COMMAND
- ESCAPE_SEQUENCE_HANDLING
test_pattern: INTERACTION_TEST
---

# du-command-pattern-filtering

## Instructions

# DU Command Pattern Filtering

## Instructions

- WHEN the TG encounters a shell command that accepts both specific table names and regex patterns as positional arguments (e.g., `du -p <pattern>`)
- THEN it should write a test that:
  1. Creates multiple test entries (e.g., tables "t" and "tt") using the shell's `createtable` command
  2. Runs the command with a regex pattern that should match only a subset (e.g., `du -p t.*(..)` where the pattern `t.*` matches everything while the additional `(..)` should restrict to two-letter suffixes)
  3. Verifies that the output contains ONLY the expected matched entry (e.g., "tt" has two chars after "t" matching `(..)`, while "t" has zero) and NOT the other entry
  4. Specifically checks that the unmatched entry's name does NOT appear in the output
- Common pitfalls to avoid:
  - Testing only with a single table name argument, missing the pattern-matching branch entirely
  - Failing to verify that unmatched entries are absent from the output (only checking presence, not absence)
  - Using a pattern that is too simple (e.g., just `t.*`) which matches everything, masking the bug
  - Forgetting that regex patterns can be anchored or contain group constraints like `(..)` that should affect matching behavior

### Example (correct):
```java
// Creates tables "t" and "tt", runs du -p t.*(..), expects only "tt" to appear
ts.createtable("t");
ts.createtable("tt");
ts.table("", "du -p t.*(..)");
ts.createtable("t3"); // additional check
ts.table("", "du -p t.*(..)");
assertShellOutputDoesNotContain("t ", ts.getOutput());
assertShellOutputContains("tt", ts.getOutput());
```

### Example (incorrect — missing absence check):
```java
ts.createtable("t");
ts.createtable("tt");
ts.table("", "du -p t.*(..)");
// FAILS: only checks 'tt' is present, does not verify 't' is absent
assertShellOutputContains("tt", ts.getOutput());
// The buggy code would show BOTH 't' and 'tt' in output
```