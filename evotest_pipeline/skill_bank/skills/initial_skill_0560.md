---
name: iteration-statement-traversal
description: When code visits/iterates over control flow statements, ensure all statement
  types within each case branch are visited, including implicit fall-through branches.
  Use this skill for SwitchCase or similar AST node traversal where statement iteration
  may skip or mishandle certain children.
code_tags:
- VALIDATION
- ITERATION_STATEMENT_VISITOR
- STATE_MUTATION
test_pattern: STATE_TEST
---

# iteration-statement-traversal

## Instructions

# Iteration Statement Traversal

## Instructions

- WHEN the TG encounters code that implements an **iterator or visitor over switch case statements** (e.g., iterating "all case statements" in a CtSwitch, or visiting statements within a case body)
- THEN the TG should test that **all nested statements in all case branches are correctly visited**, including **fall-through case groups** where one case block does not break and execution continues into the next case
- Specifically, test with a switch statement containing **multiple case labels in the same case group** (e.g., `case 1: case 2: stmt; break; case 3: stmt2; break;`), and verify that each individual statement node is visited exactly once
- Verify that the return count of visited statements equals the **total number of statements across all case blocks**, not just the statement count of a single case block
- **Common pitfall**: Testing only single-case switch statements, which does not expose problems with visit skipping; **always test at least two cases with different case values and multiple statements**
- **Example (correct test)**:
  ```java
  // Given a switch with two case groups:
  // case 1: case 2: stmt1; stmt2; break;
  // case 3: stmt3; break;
  // Then iterating all statements should return 3 statement nodes
  List<CtStatement> stmts = switchElement.getCaseStatements();
  assertEquals(3, stmts.size());
  assertTrue(stmts.contains(stmt1));
  assertTrue(stmts.contains(stmt2));
  assertTrue(stmts.contains(stmt3));
  ```
- **Example (incorrect test — misses the bug)**:
  ```java
  // Only tests a single case with one statement
  List<CtStatement> stmts = switchElement.getCaseStatements();
  assertEquals(1, stmts.size()); // Would pass even if fall-through branches are skipped
  ```
- The test should fail on the buggy version (returning fewer statements than expected) and pass on the fixed version