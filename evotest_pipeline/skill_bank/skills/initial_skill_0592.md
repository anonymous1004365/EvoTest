---
name: remove-all-statements-consistency
description: WHEN dealing with methods that remove all statements from a code element
  iteratively (e.g., by repeatedly removing the first statement), THEN test that ALL
  statements are actually removed and the element transitions to a correct empty state.
  This skill applies when collection removal operations depend on state mutation during
  iteration — a common bug pattern where removing an element shifts remaining elements
  and indexing becomes incorrect.
code_tags:
- STATE_MUTATION
- ARRAY_ITERATION
- VALIDATION
test_pattern: STATE_TEST
---

# remove-all-statements-consistency

## Instructions

# Remove-All-Statements Consistency

## Instructions

- WHEN the TG encounters a method that removes all children/statements from a code element (e.g., `CtBlock`, `CtStatementList`, or any container of statements) by repeatedly removing the "first" or "last" statement in a loop (e.g., `while (statements.size() > 0) { remove(statements.get(0)); }`)
- THEN the TG should write a test that:
  1. Creates a container with **multiple** (≥2) statements/children
  2. Calls the "remove all" method
  3. Verifies that **all** statements are removed (e.g., `container.getStatements().size() == 0` or `container.getStatements().isEmpty()`)
  4. Verifies the container no longer references any removed children (e.g., `container.getStatements()` returns an empty list)
  5. Also verifies that the **removed statements themselves** are properly detached from their parent (e.g., `statement.getParent() == null` or similar)
- Common pitfalls to avoid:
  - **Testing only with a single child** — this masks the indexing bug because with one element, the loop terminates after one iteration regardless
  - **Only checking that no exception is thrown** — the method could silently complete without removing everything
  - **Assuming remove() shifts indices correctly inside a forward-iteration loop** — `remove(i)` while `i` increments will skip elements because indices shift
  - **Not verifying the container's final state** — the bug is that the container's internal state is inconsistent (some elements removed, some not, broken parent references)

### Correct Example (Bug-detecting)

```java
// Create a block with 3 statements
CtBlock<?> block = factory.createBlock();
CtStatement stmt1 = factory.createCodeSnippetStatement("int x = 1");
CtStatement stmt2 = factory.createCodeSnippetStatement("int y = 2");
CtStatement stmt3 = factory.createCodeSnippetStatement("int z = 3");
block.addStatement(stmt1);
block.addStatement(stmt2);
block.addStatement(stmt3);

// Call the remove-all method
block.removeAllStatements();

// VERIFY: All statements are gone
assertEquals(0, block.getStatements().size());
assertTrue(block.getStatements().isEmpty());
```

### Incorrect Example (Misses the Bug)

```java
// Only testing with one child — hides the bug
CtBlock<?> block = factory.createBlock();
CtStatement stmt = factory.createCodeSnippetStatement("int x = 1");
block.addStatement(stmt);
block.removeAllStatements();

// This passes even on the buggy version
assertEquals(0, block.getStatements().size());
```