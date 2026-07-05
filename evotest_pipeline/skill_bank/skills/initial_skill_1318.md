---
name: checkpoint-retrieve-after-null-store
description: WHEN a NodeStore's retrieve() method is called with a checkpoint obtained
  from store.checkpoint() but the underlying store might be null/unset, THEN test
  that the retrieved NodeState is not null and that operations on it succeed. This
  helps catch cases where the checkpoint creation returns a valid reference but the
  store returns null on retrieval.
code_tags:
- NULL_CHECK
- VALIDATION
- CHECKPOINT_RETRIEVAL
- STATE_MUTATION
test_pattern: STATE_TEST
---

# checkpoint-retrieve-after-null-store

## Instructions

# Checkpoint Retrieval and State Mutation After Null Store

## Instructions

WHEN the TG encounters a `NodeStore` that supports `checkpoint(long lifetime, Map<String, String> properties)` and `retrieve(String checkpoint)` methods, and the test creates a checkpoint and then retrieves it:

- THEN the test should verify that the retrieved `NodeState` is NOT null immediately after `retrieve()` returns
- THEN the test should verify that operations on the retrieved `NodeState` (e.g., `exists()`, `getChildNodeCount()`, `getPropertyCount()`) complete without throwing a `NullPointerException`

Common pitfalls to avoid:
- Testing only that `checkpoint()` returns a non-null string without also verifying `retrieve()` returns a valid `NodeState`
- Assuming that because a checkpoint was successfully created, it will always be retrievable
- Testing with a single `NodeStore` type (e.g., only `SegmentNodeStore`) when the interface is used by multiple implementations
- Verifying the checkpoint exists only by checking the returned string from `checkpoint()`, not by actually calling `retrieve()` and operating on the result

**Correct example:**
```java
@Test
public void testCheckpointRetrieval() {
    NodeStore store = getNodeStore();
    String cp = store.checkpoint(TimeUnit.HOURS.toMillis(24));
    assertNotNull("Checkpoint reference must not be null", cp);
    NodeState retrieved = store.retrieve(cp);
    assertNotNull("Retrieved NodeState must not be null", retrieved);
    assertTrue("Retrieved checkpoint must exist", retrieved.exists());
    // Verify the checkpoint is a valid node state by accessing its properties
    assertTrue("Checkpoint should have child nodes", retrieved.getChildNodeCount() >= 0);
}
```

**Incorrect example (missing null/state checks):**
```java
@Test
public void testCheckpoint() {
    NodeStore store = getNodeStore();
    String cp = store.checkpoint(TimeUnit.HOURS.toMillis(24)); // Only checks cp is non-null
    assertNotNull(cp);
    // Bug: never calls retrieve(cp) to verify the checkpoint is actually retrievable
    // Bug: never verifies the retrieved node state is non-null and operational
}
```