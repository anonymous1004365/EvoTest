---
name: branch-commit-recovery-ordering
description: Tests recoverBranchCommit should ensure all pending branch operations
  are properly merged, especially when branches share commit roots. Use STATE_TEST
  to verify recovered branches reflect all expected state changes.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: STATE_TEST
---

# branch-commit-recovery-ordering

## Instructions

# Branch Commit Recovery Ordering

## Instructions

- WHEN the TG encounters a method `recoverBranchCommit()` (or similar) in a `DocumentNodeStore`-like class that merges/recovers branch commits back into the main store
- THEN it should test that after recovery, the resulting root state reflects ALL changes made during the branch commits, including:
  - Child nodes that were created in the branch
  - Properties that were modified in the branch
  - Nodes that were removed in the branch
- The test should create a branch commit (using `store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY)` or similar), and then verify the recovered state via `store.getRoot().hasChildNode(name)` and/or `store.getRoot().getChildNode(name)` returning the expected state.
- Common pitfalls to avoid:
  - Testing only that no exception is thrown during recovery — the test must check the actual state content after recovery.
  - Using `getRoot()` without first calling the recovery method (e.g., `runBackgroundOperations()` or `recoverBranchCommit()`).
  - Assuming the initial zero-state root means recovery worked — the test must create meaningful changes in the branch BEFORE recovery.

### Correct example:
```java
@Test
public void testRecoveredStateHasBranchChanges() throws Exception {
    DocumentNodeStore store = new DocumentMK.Builder()
            .setAsyncDelay(0)
            .setDocumentStore(new MemoryDocumentStore())
            .setClusterId(1)
            .getNodeStore();
    
    // Create a branch with some changes
    NodeBuilder builder = store.getRoot().builder();
    builder.child("testNode");
    builder.setProperty("testProp", "value");
    store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);
    
    // Simulate recovery (e.g., background operations)
    store.runBackgroundOperations();
    
    // Verify the changes are present after recovery
    NodeState root = store.getRoot();
    assertTrue("Branch node should exist after recovery", root.hasChildNode("testNode"));
    assertEquals("value", root.getChildNode("testNode").getProperty("testProp").getValue(Type.STRING));
    
    store.dispose();
}
```

### Incorrect example:
```java
// WRONG: Only checks no exception is thrown
@Test
public void testRecoveryNoError() throws Exception {
    DocumentNodeStore store = new DocumentMK.Builder()
            .setAsyncDelay(0)
            .setDocumentStore(new MemoryDocumentStore())
            .setClusterId(1)
            .getNodeStore();
    
    store.runBackgroundOperations();  // no changes made yet!
    // This passes even if recovery is broken — there was nothing to recover
    
    store.dispose();
}
```