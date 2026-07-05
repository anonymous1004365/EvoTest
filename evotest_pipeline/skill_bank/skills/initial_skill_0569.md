---
name: insert-before-after-switch-case
description: When inserting statements before or after elements in a CtBlock/CtCase
  within a switch-case structure, the TG should test insertion at the child caretaker
  node (switch case body) level, not the switch parent level. This skill applies when
  insertBefore/insertAfter is called on SwitchCase children or Case nodes.
code_tags:
- VALIDATION
- ARGUMENT_VALIDATION
- NULL_CHECK
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# insert-before-after-switch-case

## Instructions

# Insert Before/After in Switch Case Statements

## Instructions

- WHEN the TG encounters code that inserts statements (via `insertBefore` or `insertAfter`) into the body of a `CtCase` (switch case), which is represented as a `CtBlock` of statements owned by a case node inside a `CtSwitch`
- THEN the TG should write a test that:
  1. Creates a `CtSwitch` with multiple `CtCase` entries (each containing a `CtBlock` of statements)
  2. Obtains a reference to a specific `CtStatement` that is a direct child of the case's body `CtBlock`
  3. Calls `insertBefore(statementToInsert)` or `insertAfter(statementToInsert)` on that statement
  4. Verifies that the inserted statement appears at the correct position *within the switch case's body*, not at the switch level or elsewhere
  5. Expects the assertion to pass after the fix (the insertion should succeed and the statement list of the case block should be updated correctly); on the buggy version, the insertion may throw an exception (e.g., `ClassCastException`, `IndexOutOfBoundsException`) or insert at the wrong location

- Common pitfalls to avoid:
  - Testing only `insertBefore`/`insertAfter` on regular block statements (outside switch cases) — this skill specifically targets switch case bodies
  - Assuming that the parent-child traversal in switch-case structures follows the same path as regular block statements — the switch case's statements are children of a `CtCase`, not directly of a `CtSwitch`
  - Not checking the actual position of the inserted statement after the operation (verify size and order of `case.getBody().getStatements()`)
  - Forgetting to build a proper `CtSwitch` with at least two `CtCase` entries so that insertion positioning matters

- Example of a correct test:
```java
// Create a switch with two case blocks
CtSwitch<?> switchStmt = factory.createSwitch();
CtCase case1 = factory.createCase();
CtCase case2 = factory.createCase();
CtBlock<?> block1 = factory.createBlock();
CtBlock<?> block2 = factory.createBlock();
CtStatement stmtA = factory.createCodeSnippetStatement("a()");
CtStatement stmtB = factory.createCodeSnippetStatement("b()");
block1.addStatement(stmtA);
block2.addStatement(stmtB);
case1.setBody(block1);
case2.setBody(block2);
switchStmt.getCases().add(case1);
switchStmt.getCases().add(case2);

// Insert before a statement inside case1's body
CtStatement inserted = factory.createCodeSnippetStatement("inserted()");
// This should succeed: stmtA is a child of block1 which is the body of case1
stmtA.insertBefore(inserted);

// Verify
assertEquals(2, block1.getStatements().size());
assertEquals(inserted, block1.getStatements().get(0));
assertEquals(stmtA, block1.getStatements().get(1));
```

- Example of an incorrect test (too shallow):
```java
// WRONG: Only tests insertBefore on regular block statements
CtBlock block = factory.createBlock();
CtStatement stmt = factory.createCodeSnippetStatement("x()");
block.addStatement(stmt);
stmtA.insertBefore(otherStmt); // This works in general but misses the switch case edge case
```