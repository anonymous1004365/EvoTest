---
name: checkpoint-retrieve-null-for-unknown
description: When testing NodeStore.checkpoint() and retrieve() methods, verify that
  retrieving an unknown/non-existent checkpoint returns null and that release() returns
  true for non-existent checkpoints. This skill prevents fragile tests that assume
  all NodeStore implementations behave identically.
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
- NULL_CHECK
test_pattern: STATE_TEST
---

# checkpoint-retrieve-null-for-unknown

## Instructions

# Checkpoint Retrieve Returns Null for Unknown References

## Instructions

- WHEN testing the `NodeStore.retrieve(String checkpoint)` method with a non-existent or unknown checkpoint reference
- THEN verify that `store.retrieve("r42-0-0")` returns `null` (not throwing an exception, and not returning a non-null NodeState). Use `assertNull(store.retrieve(...))` to make the assertion explicit.
- WHEN testing the `NodeStore.release(String checkpoint)` method with a non-existent checkpoint
- THEN verify that `store.release("some-nonexistent-checkpoint")` returns `true` (as specified in the `NodeStore` interface contract: "Returns true if the checkpoint was successfully removed, or if it doesn't exist")
- WHEN creating a checkpoint test that works across multiple NodeStore implementations (e.g., `MemoryNodeStore`, `SegmentNodeStore`, `DocumentNodeStore`)
- THEN test with both the specific `NodeStore` implementation type AND the generic `NodeStore` interface to catch implementation-specific bugs
- WHEN checking the state after checkpoint operations, after calling `store.checkpoint(...)`, verify that `store.getRoot()` returns the same state as before (creating a checkpoint should NOT change the root state). Compare via `assertEquals(root, store.getRoot())` where `root` was captured before the checkpoint call.
- Common pitfalls to avoid:
  - DO NOT assume that `store.retrieve("r42-0-0")` should throw an exception — the contract says it returns null
  - DO NOT test only with valid checkpoint references — always also test with invalid/malformed references
  - DO NOT skip testing the `release` method's behavior for non-existent checkpoints — the contract says it returns true
  - DO NOT assume `store.checkpoint(...)` preserves the root unchanged if the implementation captures the root state at the time of checkpoint creation — verify explicitly

### Correct Example (from CheckpointTest.retrieveAny):
```java
@Test
public void retrieveAny() {
    assertNull(store.retrieve("r42-0-0"));
}
```

### Correct Example (from CheckpointTest.checkpoint):
```java
@Test
public void checkpoint() throws CommitFailedException {
    String cp = store.checkpoint(Long.MAX_VALUE);
    
    NodeBuilder builder = store.getRoot().builder();
    builder.setChildNode("new");
    store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);
    
    assertFalse(root.equals(store.getRoot()));
    assertEquals(root, store.retrieve(cp));
    
    assertTrue(store.release(cp));
    assertNull(store.retrieve(cp));
}
```

### Incorrect Example (fragile assumption):
```java
// BAD: Assumes retrieve throws exception for unknown reference
@Test(expected = IllegalArgumentException.class)
public void retrieveAny() {
    store.retrieve("r42-0-0");
}

// BAD: Doesn't check return value of release for non-existent checkpoints
@Test
public void testRelease() {
    store.release("nonexistent");  // No assertion!
}
```