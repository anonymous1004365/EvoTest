---
name: muatble-tree-status-tracking
description: When a MutableTree is obtained, then later re-obtained after a rebase/refresh,
  the status of child nodes (NEW vs UNCHANGED) should be re-evaluated. Test that child
  trees added via addChild and then re-fetched from a fresh root still report the
  correct status.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# muatble-tree-status-tracking

## Instructions

# MutableTree Status Tracking After Root Refresh

## Instructions

**WHEN** the test obtains a `MutableTree` from a `MutableRoot`, adds a child via `addChild("childName")`, then calls `root.rebase()` (or `root.refresh()`) to obtain a new tree object, and then calls `getStatus()` or `isNew()` on the child:

- **THEN** the TG MUST verify that the re-fetched tree correctly returns `Tree.Status.NEW` for the child node (not `Tree.Status.UNCHANGED`).
- **THEN** the TG MUST assert the status of the added child node after each state mutation (addChild, rebase/refresh, getChild), not just once.
- **THEN** the TG MUST use both `getStatus()` and `isNew()` assertions (when applicable) to catch inconsistent behavior.
- **THEN** the TG MUST test with a `CommitFailedException` handling pattern since operations like `rebase()` can throw.

**Common pitfalls:**
- ❌ Testing `getStatus()` only on the original tree object before rebase — this misses the bug.
- ❌ Assuming that after `rebase()` or `refresh()`, the old tree reference remains valid — the TG should fetch a new child tree from the new root.
- ❌ Not distinguishing between `isNew()` semantics (relative to the builder's base state) vs `getStatus()` semantics (relative to the persisted state).
- ❌ Testing only a single state transition — the bug manifested when the status was checked after `root.rebase()` followed by fetching the child again from the new parent tree.

**Correct example (catches the bug):**
```java
@ParameterizedTest
@ValueSource(booleans = {true, false})
void isNew(boolean skipRebase) throws CommitFailedException {
    MutableRoot root = new MutableRoot(...);
    Tree tree = root.getTree("/");
    tree.addChild("new");
    tree.getChild("new").setProperty("test", "value");
    assertEquals(Tree.Status.NEW, tree.getChild("new").getStatus());

    if (!skipRebase) {
        root.rebase();
        tree = root.getTree("/");
    }

    // Bug: after rebase, status incorrectly shows UNCHANGED instead of NEW
    assertEquals(Tree.Status.NEW, tree.getChild("new").getStatus());
}
```

**Incorrect example (would miss the bug):**
```java
@Test
void isNew() throws CommitFailedException {
    MutableRoot root = new MutableRoot(...);
    Tree tree = root.getTree("/");
    tree.addChild("new");
    assertEquals(Tree.Status.NEW, tree.getChild("new").getStatus());
    // Bug: only tests before rebase, never re-fetches the tree
    // after the root is re-based
}
```