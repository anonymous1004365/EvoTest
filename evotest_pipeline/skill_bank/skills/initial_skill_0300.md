---
name: nodebuilder-rebase-state-order
description: When a NodeBuilder has child nodes that are modified before a rebase
  operation, the rebase must correctly merge those modifications. This skill teaches
  how to test that rebase correctly preserves changes made to child nodes after rebase.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# nodebuilder-rebase-state-order

## Instructions

# NodeBuilder Rebase Must Preserve Child Modifications

## Instructions

- WHEN the TG encounters code that implements a `NodeBuilder` interface where child nodes can be added/modified and then a `rebase()` operation is called on the builder:
  - THEN the TG should write a test that:
    1. Creates a root `NodeBuilder`
    2. Adds a child node (e.g., by calling `builder.child("x")`)
    3. Gets a reference to that child node
    4. Calls `builder.rebase()` (or a method that triggers a rebase)
    5. Modifies the child node (e.g., adds a sub-child via `child.child("y")`)
    6. Calls `builder.rebase()` again
    7. Asserts that the child node's modifications are still present after the second rebase
  - The test should verify that after the second rebase, calling `child.getChildNode("y")` returns a non-null result.
  - The expected behavior on the buggy version: the child's modifications (e.g., added sub-child) are lost after rebase, causing `getChildNode("y")` to return `null` or an unexpected state.

- Common pitfalls to avoid:
  - Testing only rebase on the root builder without making child modifications before rebase
  - Testing only modifications made directly on the root builder, not on a separately-referenced child node
  - Using a single rebase call when the bug is triggered by the sequence: add child → rebase → modify child → rebase
  - Not comparing the state of a child node reference held before the first rebase vs. after the second rebase

## Examples

**Correct test pattern** (catches this bug):
```java
NodeBuilder builder = root.builder();
NodeBuilder child = builder.child("x");
builder.rebase();
child.child("y");  // modify child after first rebase
builder.rebase();  // second rebase
assertNotNull(child.getChildNode("y"));  // should still be present
```

**Incorrect test pattern** (misses this bug):
```java
NodeBuilder builder = root.builder();
builder.child("x");
builder.rebase();
// only tests root-level modifications, not child references
assertNotNull(builder.getChildNode("x"));
```

**Another incorrect pattern** (misses this bug):
```java
NodeBuilder builder = root.builder();
NodeBuilder child = builder.child("x");
child.child("y");  // modify child BEFORE rebase
builder.rebase();
assertNotNull(child.getChildNode("y"));  // this may pass even on buggy version
// missing the second rebase that triggers the bug
```