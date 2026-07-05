---
name: shell-command-pattern-parameter-validation
description: Guide for writing tests that validate shell commands or string-splitting
  methods accepting pattern-type parameters when they contain regex metacharacters.
  Use when testing commands that accept user-provided patterns/paths that may include
  wildcards, or when testing String.split() with custom separators that may contain
  regex metacharacters.
code_tags:
- VALIDATION
- STATE_MUTATION
- STRING_SPLIT
- REGEX_ESCAPE
- PATTERN_QUOTE
test_pattern: EXCEPTION_TEST
retrieval:
  keywords: []
  boosted_tags: []
  suppressed_tags: []
  negative_triggers: []
  applicable_tiers: []
  transition_tags: []
---

# shell-command-pattern-parameter-validation

## Instructions

# Shell Command Pattern Parameter Validation

## Instructions

- WHEN the TG encounters a shell command (like `du`, `ls`, `grep`, `rm`) that accepts a pattern parameter (e.g., `-p` flag with a regex/wildcard)
- THEN it should test that the command correctly handles patterns containing regex metacharacters (`.`, `*`, `?`, `+`, `[`, `]`, `(`, `)`, etc.) that can match unexpected or additional results
- Include concrete values from the actual codebase: e.g., the `du` command with `-p t.*` should produce exactly `0 [t, tt]` output, not include extra results like `0 [t, tt] present in ylyu@fake tt> du -p t.*(..)`
- The test should verify that when a pattern like `t.*` is used, only exact matches for the pattern are returned — not partial or overlapping matches caused by shell/reserved characters
- Common pitfalls to avoid:
  - Testing only with simple literals (e.g., `du -p t`) — this masks regex metacharacter issues
  - Testing only with the exact table names, not with patterns that could match differently
  - Assuming pattern matching is plain string matching rather than regex-based
  - Not including both the table creation pattern and the command execution in the same test
- Example of a correct test pattern:
  ```java
  // Create tables whose names form overlapping matching patterns
  ts.exec("createtable t", true, "", true, null);
  ts.exec("createtable tt", true, "", true, null);
  // Execute the command with a regex pattern that should only match 't'
  ts.exec("du -p t.*", true, "0 [t, tt]", true, null);
  // On buggy versions, this may return extra results like "0 [t, tt] present..."
  ```
- Example of an incorrect/insufficient test:
  ```java
  // WRONG: Tests only with exact literal name, not with regex patterns
  ts.exec("createtable myTable", true, "", true, null);
  ts.exec("du -p myTable", true, "0 [myTable]", true, null); // No regex metacharacters tested
  ```