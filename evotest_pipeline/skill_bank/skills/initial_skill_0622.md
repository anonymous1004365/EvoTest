---
name: statement-removal-validates-block-list
description: When removing an element from an observable list that has a listener,
  the listener may attempt to access the list which is in an inconsistent state. Tests
  must verify list integrity after removal operations on observable collections with
  attached listeners.
code_tags:
- STATE_MUTATION
- COLLECTION_MODIFICATION_DURING_ITERATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# statement-removal-validates-block-list

## Instructions

# Statement Removal Validates Block List Integrity

## Instructions

WHEN the TG encounters a method that removes an element from a list (e.g., `CtBlock.removeStatement(CtStatement)`) and the list has associated listeners or watchers that may be notified during removal:

- THEN the test MUST verify that after removing one statement from a block containing multiple statements, the remaining statements in the block's statement list are still accessible and have not been corrupted (returning null or throwing exceptions)
- THEN use a state-based test that: (1) creates a block with 2+ statements, (2) removes exactly one of them using the removal method, (3) iterates over all remaining statements and asserts they are non-null, and (4) verifies the size of the list is decremented by exactly 1
- THEN assert the specific expected behavior: after removal, `getStatements()` should return a list where all elements are non-null and the removed element is absent
- THEN expect that the buggy version will cause `IndexOutOfBoundsException`, `NullPointerException`, or produce a list with null entries when iterating over the remaining statements after removal

Common pitfalls:
- Testing removal only on a single-element block (won't trigger the iteration corruption)
- Testing removal without checking the integrity of all remaining elements in the list
- Checking only the size of the list without verifying each element is non-null and accessible
- Testing removal by reference (object identity) when the method might use index-based removal that confuses listener notifications

Example (correct):
```java
// Test that after statement removal, remaining statements are valid
CtBlock<?> block = factory.createBlock();
CtStatement stmt1 = factory.createCtStatement();
CtStatement stmt2 = factory.createCtStatement();
// ... add both statements ...
block.addStatement(stmt1);
block.addStatement(stmt2);
assertEquals(2, block.getStatements().size());

block.removeStatement(stmt1);
assertEquals(1, block.getStatements().size());
// Verify remaining elements are not null/corrupted
for (CtStatement remaining : block.getStatements()) {
    assertNotNull("Remaining statement should not be null after removal", remaining);
}
```

Example (incorrect — won't catch the bug):
```java
// Only tests with single element — doesn't exercise the iteration issue
CtBlock<?> block = factory.createBlock();
CtStatement stmt = factory.createCtStatement();
block.addStatement(stmt);
block.removeStatement(stmt);
assertEquals(0, block.getStatements().size()); // Passes even with the bug
```