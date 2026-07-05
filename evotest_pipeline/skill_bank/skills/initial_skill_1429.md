---
name: child-node-combined-delete-and-add-comparison
description: Teaches the TG to test that compareAgainstBaseState correctly handles
  scenarios where a child node is deleted and multiple new child nodes are added in
  the same state transition, catching iterator ordering bugs that cause subsequent
  child records to be misread.
code_tags:
- COMPARISON_LOGIC
- DELETED_AND_ADDED_CHILD_NODE
- CHILD_NODE_ENUMERATION
test_pattern: PARAMETRIC_TEST
---

# child-node-combined-delete-and-add-comparison

## Instructions

# Child Node Combined Delete and Add Comparison

## Instructions

- WHEN the TG is testing a `compareAgainstBaseState()` method that compares two node states using `NodeStateDiff`, and the state transition involves both deleting an existing child node AND adding new child nodes in a single update
  - THEN the TG MUST create a test that performs all of these operations on the same `NodeBuilder` (or equivalent mutable state holder) before calling `getNodeState()`: remove an existing child node, add at least two new child nodes, then call `compareAgainstBaseState(before, diff)` and verify that ALL `childNodeDeleted`, `childNodeAdded`, etc. callbacks fire on the diff mock with the correct arguments.
  - The TG MUST verify the correctness of the diff callback expectations by:
    1. Expecting `childNodeDeleted("baz", ...)` for the removed child node, and `childNodeAdded(name, after.getChildNode(name))` for EACH newly added child node.
    2. Using `after.getChildNode(name)` (not `before.getChildNode(name)`) when setting up expectations for `childNodeAdded`.
    3. Ensuring the mock is set up with exact expected return values (`expect(...).andReturn(true)`) for each callback.
    4. Calling `replay(diff)` and then `after.compareAgainstBaseState(before, diff)`, followed by `verify(diff)`.
  - Common pitfalls to avoid:
    - **Incorrect child node reference**: When setting up the `childNodeAdded` expectation, use `after.getChildNode(name)` — NOT `before.getChildNode(name)` — since the child node doesn't exist in the `before` state.
    - **Only testing individual operations**: A test that only deletes a child node OR only adds child nodes will NOT catch this bug. You MUST combine both operations in the same state transition (delete one child, add multiple new children).
    - **Incorrect mock return value**: The `expect(...).andReturn(true)` is required on each diff mock expectation because the comparison might stop early if `false` is returned.
    - **Wrong child node name in assertion**: When adding multiple children, ensure each `childNodeAdded` assertion uses the correct name (e.g., `"x"` and `"y"`), not the same name for both.

- **Correct example** (catches the bug):
```java
@Test
public void testChildNodeDeletedAndMultipleAdded() {
    NodeState before = builder.getNodeState();
    builder.getChildNode("baz").remove();
    builder.child("x");
    builder.child("y");
    NodeState after = builder.getNodeState();

    expect(diff.childNodeDeleted("baz", before.getChildNode("baz"))).andReturn(true);
    expect(diff.childNodeAdded("x", after.getChildNode("x"))).andReturn(true);
    expect(diff.childNodeAdded("y", after.getChildNode("y"))).andReturn(true);  // NOT after.getChildNode("x")
    replay(diff);

    after.compareAgainstBaseState(before, diff);
    verify(diff);
}
```

- **Incorrect example** (does NOT catch the bug):
```java
@Test
public void testChildNodeDeleted() {
    NodeState before = builder.getNodeState();
    builder.getChildNode("baz").remove();
    NodeState after = builder.getNodeState();

    expect(diff.childNodeDeleted("baz", before.getChildNode("baz"))).andReturn(true);
    replay(diff);
    after.compareAgainstBaseState(before, diff);
    verify(diff);
}
// Above only tests deletion alone, missing the combined delete+add scenario
```