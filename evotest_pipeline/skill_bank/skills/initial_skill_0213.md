---
name: document-node-store-uncommitted-changes-ignored
description: When testing document node store operations that involve background update
  threads or pending changes, the TG should verify that uncommitted or orphaned changes
  are correctly ignored rather than counted. This skill covers testing edge cases
  where internal collections may retain stale state from previous operations.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
- CONCURRENCY
test_pattern: STATE_TEST
---

# document-node-store-uncommitted-changes-ignored

## Instructions

# Document Node Store Uncommitted Changes Ignored

## Instructions

- WHEN the TG encounters a method that reports the count of pending or uncommitted changes (e.g., `getPendingWriteCount()`, `getUnmergedBranchCount()`, or similar aggregation methods that sum over internal collections)
- THEN the TG should test that after committing OR discarding all pending changes via the appropriate API (e.g., committing the merge, calling `revert()`, or discarding the branch), the count correctly returns to zero
  - Specifically, test the scenario where:
    1. A change is made (e.g., adding a node or updating a property)
    2. The change is then undone/rolled back (e.g., via `revert()` or abandoning the uncommitted state)
    3. The count method returns 0, not 1
  - The expected behavior on the buggy version is that the count returns 1 (stale uncommitted entry), while on the fixed version it returns 0
- Common pitfalls:
  - Testing only the happy path where changes are committed and counts increase, without testing the rollback/discard case
  - Assuming that reverting or discarding changes cleans up all internal counters — the TG should explicitly verify this
  - Not accounting for background merge/rebase threads that may modify internal state after the revert
  - Using single-threaded test setup when the actual code uses background threads — the TG should ensure proper synchronization or use test seams to control background operations

**Example (correct test):**
```java
// Setup
DocumentNodeStore store = ...;
// Create a session and make an uncommitted change
NodeState root = store.getRoot();
NodeBuilder builder = root.builder();
builder.child("test");
// Revert the change without merging
// Then verify the pending count is 0
// (The buggy version would return 1 here)
assertEquals(0, store.getPendingWriteCount());  // FAILS on buggy version
```

**Example (incorrect test — misses the bug):**
```java
DocumentNodeStore store = ...;
// Only test that the count increases after making changes
// But never tests the rollback/revert case
NodeState root = store.getRoot();
NodeBuilder builder = root.builder();
builder.child("test");
// Only verifying the happy path
assertTrue(store.getPendingWriteCount() > 0);  // Does NOT catch the bug
```