---
name: tree-removal-status-check
description: When testing tree node removal, the TG should verify that operations
  on a removed tree node throw an appropriate IllegalStateException, because the node
  no longer has a valid base state. This skill ensures tests cover the post-removal
  state of child nodes after removing a parent.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# tree-removal-status-check

## Instructions

# Tree Removal Node Status Validation

## Instructions

- WHEN the TG encounters code that removes a parent tree node (e.g., `tree.remove()`) and later accesses properties or status of a child node that was obtained as a Tree reference **before** the parent was removed
- THEN the TG should test that accessing the child tree's status or state after its parent has been removed throws an `IllegalStateException`
- Specifically, call `child.getStatus()` on a child Tree reference obtained before calling `parent.remove()`, and verify that the operation on the removed child tree throws `IllegalStateException` with a message containing "Cannot get the base state of a removed tree"
- The TG should also test that calling `parent.getStatus()` after `parent.remove()` returns `Status.REMOVED` (i.e., the parent's status is properly updated)
- Common pitfalls to avoid:
  - Testing only `parent.getStatus()` after removal without also checking the child reference that became stale
  - Assuming that a child Tree reference is still usable after its parent is removed
  - Testing only `tree.exists()` or `tree.getChild()` after removal without checking `getStatus()` or accessing the base state
  - Not checking the specific exception type (`IllegalStateException`) or the exact error message

### Example (Correct Test)

```java
@Test
public void nodeStatus() throws CommitFailedException {
    Tree tree = root.getTree("/");
    Tree added = tree.addChild("added");
    root.commit();

    Tree n1 = added.addChild("n1");
    assertEquals(Status.NEW, n1.getStatus());

    // After removing the parent "added", accessing the child "n1" should fail
    added.remove();
    assertThrows(IllegalStateException.class, () -> n1.getStatus());

    // The removed parent itself should report REMOVED status
    assertEquals(Status.REMOVED, added.getStatus());
}
```

### Example (Incorrect Test — Missing Child Check)

```java
@Test
public void nodeStatus_partial() throws CommitFailedException {
    Tree tree = root.getTree("/");
    Tree added = tree.addChild("added");
    root.commit();

    Tree n1 = added.addChild("n1");
    assertEquals(Status.NEW, n1.getStatus());

    added.remove();
    // BUG: Only checks parent status, misses child reference check
    assertEquals(Status.REMOVED, added.getStatus());
    // Should also verify n1.getStatus() throws IllegalStateException
}
```