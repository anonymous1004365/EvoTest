---
name: authorization-sorting-and-grep-test
description: WHEN testing shell commands that handle user authorizations (auths),
  THEN verify that output is sorted alphabetically and that grepping for partial output
  strings correctly validates the full result. This skill prevents bugs where unsorted
  authorization output is silently accepted by tests that only grep for partial content.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- AUTHS_SORTING_OUTPUT
test_pattern: STATE_TEST
---

# authorization-sorting-and-grep-test

## Instructions

# Authorization Sorting and Grep Test Skill

## Instructions

- WHEN the TG encounters a shell command that outputs user authorizations (like `getauths` in an Accumulo shell command) or any command whose output is a comma-separated list of items,
  - THEN the TG must write a test that (1) calls the command, (2) captures the full output string, (3) verifies the authorizations appear in **sorted alphabetical order** (e.g., "x,y,z" not "y,z,x").
  - The test should parse the comma-separated list output, convert to a list, and assert that the list equals its own sorted copy.
  - Additionally, the TG must avoid verifying the output only by grepping for substrings (e.g., checking that `"x"`, `"y"`, `"z"` each appear somewhere in the output) — this is insufficient because it would pass even if the output is unsorted (e.g., `"y,z,x"` contains all three letters).
  - The TG should also verify that the **output matches an expected fully-formed string**, not just fragments.
- Common pitfalls:
  - Writing a test that only checks `output.contains("x") && output.contains("y") && output.contains("z")` — this passes on both sorted and unsorted output, missing the bug.
  - Writing a test that checks `output.equals("x,y,z")` without first ensuring the command actually runs and the output is captured properly (use a shell exec mock or real shell interaction).
  - Not accounting for newlines or whitespace in the output — trim the output before comparison.
- Example (correct):
  ```java
  // Given authorizations "x", "y", "z" are set for user "test"
  exec("setauths -u test -s x,y,z");
  String output = exec("getauths -u test");
  // Expected: sorted alphabetically
  assertEquals("x,y,z", output.trim());
  // Or more robustly:
  String[] parts = output.trim().split(",");
  List<String> auths = Arrays.asList(parts);
  List<String> sorted = new ArrayList<>(auths);
  Collections.sort(sorted);
  assertEquals(sorted, auths);
  ```
- Example (incorrect — misses the bug):
  ```java
  exec("setauths -u test -s x,y,z");
  String output = exec("getauths -u test");
  // This passes for both "x,y,z" and "y,z,x" — BUG HIDDEN
  assertTrue(output.contains("x"));
  assertTrue(output.contains("y"));
  assertTrue(output.contains("z"));
  ```