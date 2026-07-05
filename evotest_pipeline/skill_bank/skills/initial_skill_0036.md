---
name: rebase-with-failed-merge-state-recovery
description: When testing rebase operations that are followed by a failed merge, the
  TG should verify that the branch state is properly reset after the merge failure.
  The test must ensure that a subsequent merge attempt on the rebased branch succeeds
  and produces the expected final state.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
- CONCURRENCY
test_pattern: STATE_TEST
---

# rebase-with-failed-merge-state-recovery

## Instructions

# Rebase with Failed Merge State Recovery

## Instructions

- WHEN the TG encounters a `NodeStore` implementation where `rebase()` is called on a branch before a `merge()` that is expected to fail (e.g., due to concurrent modification or conflicting changes)
- THEN the TG should test that after a failed merge, the branch head/base state is correctly re-established so that a subsequent merge can succeed. Specifically:
  - Create two separate branches (branchA and branchB) from the same root
  - Make conflicting modifications (e.g., branchA removes a child node, branchB modifies the same child node)
  - Merge branchA successfully first
  - Call `merge()` with `EmptyHook` on branchB and expect it to throw a `CommitFailedException` with `MERGE` type (code 2, message "Failed to merge branch")
  - After catching the exception, call `rebase()` on branchB to bring it up to date with the new root
  - THEN call `merge()` again on the rebased branch — this should succeed without throwing any exception
  - Verify the resulting root state contains the expected changes from both branches
  - **Common pitfalls:**
    - Not catching the `CommitFailedException` and treating the test as a failure instead of testing the recovery path
    - Assuming that after a failed merge, the branch is permanently broken and cannot be recovered via rebase
    - Testing only one branch in isolation (no concurrent modification) — the bug only manifests when another branch changes the base in between

### Correct Example:
```java
// Create two builders from the same root
NodeBuilder builderA = store.getRoot().builder();
NodeBuilder builderB = store.getRoot().builder();

// Make conflicting changes
builderA.getChildNode("test").getChildNode("x").remove(); // A removes x
builderB.getChildNode("test").getChildNode("x").setProperty("p", 42); // B modifies x

// Merge A first
store.merge(builderA, EmptyHook.INSTANCE, null);

// B's merge should fail
try {
    store.merge(builderB, EmptyHook.INSTANCE, null);
    fail("Expected CommitFailedException");
} catch (CommitFailedException e) {
    assertEquals(MERGE, e.getType());
}

// Rebase B and merge again - this should succeed
NodeBuilder rebased = store.getRoot().builder();
rebased.setChildNode("test", builderB.getNodeState().getChildNode("test"));
store.merge(rebased, EmptyHook.INSTANCE, null);

// Verify the final state
NodeState root = store.getRoot();
assertFalse(root.getChildNode("test").hasChildNode("x")); // removed by A
assertEquals(42, root.getChildNode("test").getChildNode("x")
    .getProperty("p").getValue(LONG)); // modified by B (after rebase)
```

### Incorrect Example (missing recovery test):
```java
// Only tests the failure but doesn't verify recovery
NodeBuilder builderA = store.getRoot().builder();
NodeBuilder builderB = store.getRoot().builder();
builderA.getChildNode("test").getChildNode("x").remove();
builderB.getChildNode("test").getChildNode("x").setProperty("p", 42);
store.merge(builderA, EmptyHook.INSTANCE, null);
try {
    store.merge(builderB, EmptyHook.INSTANCE, null);
    fail("Expected CommitFailedException");
} catch (CommitFailedException e) {
    // Missing: test that rebase + merge recovers correctly
}
```