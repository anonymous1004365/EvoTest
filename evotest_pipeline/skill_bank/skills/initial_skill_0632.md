---
name: child-node-removal-after-parent-move
description: When a child node builder is obtained from a parent builder, and the
  parent then moves or replaces its children, previously obtained child builders may
  retain stale references. Tests should verify that child nodes obtained before a
  parent update are properly invalidated or removed.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# child-node-removal-after-parent-move

## Instructions

# Child Node Invalidated After Parent Mutation

## Instructions

- WHEN the TG encounters a `NodeBuilder` (or similar hierarchical builder) that provides a `child(String name)` method returning a child builder, AND the parent builder has operations like `setChildNode(...)` that can replace child nodes at the same path
- THEN the TG should test that a child builder obtained BEFORE a parent mutation is STALE/INVALIDATED after the parent is modified. Specifically:
  - Build a tree structure: create root builder, add a child node named "x", add a grandchild "y" under "x", and a great-grandchild "z" under "y"
  - Get the child builder for path "x/y/z" (obtain deeply nested reference)
  - On the root builder, call `setChildNode("x", ...)` to replace the child "x" with a new node state (or otherwise mutate the parent to invalidate the old subtree)
  - After the mutation, assert that `builder.child("x").child("y").child("z").exists()` returns `false` — i.e., the old child path is no longer valid under the new parent state
  - Also assert that `builder.child("x").getChildNodeCount()` or similar methods reflect the replacement (the child "x" should now be the new node, which has no children "y"/"z")
- Common pitfalls to avoid:
  - ❌ Testing only with flat (single-level) child nodes — the bug manifests with NESTED child paths obtained before a parent replacement
  - ❌ Testing that a child builder still works after parent mutation (e.g., checking `exists()` returns true on the stale reference) — the stale child should be invalidated
  - ❌ Not calling `setChildNode` with a different value — the replacement must actually change the node state at that path
  - ❌ Assuming that obtaining a child builder and then modifying the parent should preserve the child — after parent mutation, previously obtained child builders should become stale

### Correct example:
```java
NodeBuilder builder = EMPTY_NODE.builder();
builder.child("x").child("y").child("z");  // create nested path
// Before mutation, x/y/z exists
assertTrue(builder.child("x").child("y").child("z").exists());
// Replace child "x" with a new empty node
builder.setChildNode("x", EMPTY_NODE);
// After replacement, old grandchildren should be gone
assertFalse(builder.child("x").child("y").exists());
assertFalse(builder.child("x").child("y").child("z").exists());
// The cached child builder for x/y/z should reflect the new state
```

### Incorrect example (pitfall to avoid):
```java
NodeBuilder builder = EMPTY_NODE.builder();
builder.child("x").child("y").child("z");
// Only test flat removal
builder.child("x").remove();
assertFalse(builder.child("x").exists());
// ❌ This tests remove(), not setChildNode() replacement
// ❌ Does not verify that deeply nested stale references are invalidated
```