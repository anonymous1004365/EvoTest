---
name: tree-after-removal-status-validation
description: When a Tree node is removed, its in-memory Tree instance should transition
  to a disconnected/non-existing state. After remove(), getStatus() should not return
  NEW, and exists() should return false. Test this on newly-added child nodes that
  are removed immediately.
code_tags:
- STATE_MUTATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# tree-after-removal-status-validation

## Instructions

# Tree Node Removal Status Validation

## Instructions

- WHEN the TG encounters code that creates a `Tree` node (via `addChild(String name)`) and then calls `remove()` on it (or on the same reference retrieved via `getChild(name)`)
- THEN the TG should verify that after `remove()`, calling `getStatus()` on a reference to the removed node returns `Status.UNCHANGED` or `Status.MODIFIED` (not `Status.NEW`), and `exists()` returns `false`. The Tree API's `Status` enum includes `UNCHANGED`, `NEW`, and `MODIFIED` — but after removal, the status should reflect that the node is no longer pending in any transitional state.
- Specifically: after adding a child node (e.g., `tree.addChild("new")`), the newly-created in-memory `Tree` reference `t` has `Status.NEW`. If `tree.getChild("new").remove()` is then called, the in-memory reference `t` must have `exists() == false`. On the **buggy** version, `t.getStatus()` incorrectly returns `Status.NEW` instead of the correct non-existing state.
- The TG should write a test that:
    1. Adds a child node to a parent `Tree` and stores the returned reference.
    2. Removes that child node via the parent (e.g., `parent.getChild("new").remove()`).
    3. Verifies the original reference returns `false` for `exists()`.
    4. Optionally verifies status is not `Status.NEW` after removal.
- Common pitfalls:
    - Testing removal only on nodes that existed before the session (persisted nodes), not on newly-added nodes. The bug specifically manifests with `NEW` nodes.
    - Relying on `getChild("new").exists()` after remove without checking the original `Tree` reference. The original `Tree` object may still reference stale in-memory state.
    - Not verifying both the original reference and the `getChild()` retrieval after remove.

## Example (correct pattern)

```java
// Correct: verifies behavior on a NEW node after remove
Tree tree = root.getTree("/");
Tree t = tree.addChild("new");     // t.getStatus() == Status.NEW
tree.getChild("new").remove();      // remove via parent
assertFalse(t.exists());            // FAILS on buggy: still NEW
assertFalse(tree.getChild("new").exists());
```

## Example (incorrect pattern)

```java
// Incorrect: only tests removal of a persisted node, misses the NEW node bug
Tree tree = root.getTree("/");
// z is a persisted node from setUp
tree.getChild("z").remove();
assertFalse(tree.getChild("z").exists());  // passes on both versions
// Does NOT test remove() on a newly-added (NEW) node
```