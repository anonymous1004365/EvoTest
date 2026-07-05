---
name: async-index-checkpoint-cleanup
description: When testing async index update lifecycle, verify that checkpoints are
  properly released/reclaimed even when no index changes occur. The TG should test
  that the `closeAndWait()` or lifecycle cleanup correctly releases resources (checkpoints)
  that were acquired during initialization.
code_tags:
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# async-index-checkpoint-cleanup

## Instructions

# Async Index Checkpoint Cleanup Resource Leak

## Instructions

**WHEN** the TG encounters code that manages checkpoint lifecycle in an async index update (a class that extends/implements `AsyncIndexUpdate` or similar pattern where a `checkpoint` is acquired via `nodeStore.checkpoint(…)` during `run()` or similar lifecycle method, and there is a `close()` / `closeAndWait()` / cleanup method that should release the checkpoint),

**THEN** the TG should write a test that:

1. **Verifies the checkpoint was acquired during the async run** — after calling `run()` (or the lifecycle trigger like `indexUpdate.run()`), assert that an initial checkpoint exists (e.g., via `getCheckpoint()` or checking the node store's checkpoint references). If the checkpoint is not created, the test should fail with a message like "Expecting the initial checkpoint".

2. **Verifies the checkpoint is released after cleanup** — after calling `closeAndWait()` (or equivalent cleanup method), assert that the checkpoint has been released (e.g., `getCheckpoint()` returns `null` or the checkpoint is no longer in the node store).

3. **Tests the case where no index changes occurred** — the scenario where the async update runs but no modifications are made to the content. This is the edge case that can expose resource leaks (the checkpoint reference may leak despite no work being done).

**Common pitfalls to avoid:**
- ❌ Testing only the success case where index updates modify data, missing the "no changes" edge case where resources may not be cleaned up
- ❌ Forgetting to call cleanup methods (like `closeAndWait()`) after the async run and only asserting checkpoint creation without asserting cleanup
- ❌ Assuming that because no work was done, no resources were allocated — the checkpoint may still have been allocated and must be released
- ❌ Failing to await asynchronous completion before asserting cleanup state

### Correct example:

```java
public void cpCleanupNoChanges() throws Exception {
    // Initialize with a checkpoint that is about to expire (or any state)
    // ... setup code ...
    
    // Run the async index update (no content changes)
    indexUpdate.run();
    
    // Assert checkpoint was created during the run
    assertNotNull("Expecting the initial checkpoint", indexUpdate.getCheckpoint());
    
    // Close and wait for cleanup
    indexUpdate.closeAndWait();
    
    // Assert checkpoint was released after cleanup
    assertNull("Checkpoint should be null after cleanup", indexUpdate.getCheckpoint());
}

// Alternatively, for async lifecycle:
public void cpCleanupNoChanges() throws Exception {
    // Initialize
    Preconditions.checkNotNull(initialCheckpoint);
    
    // Run
    Runnable r = () -> { indexUpdate.run(); };
    ExecutorService executor = Executors.newSingleThreadExecutor();
    Future<?> future = executor.submit(r);
    future.get(5, TimeUnit.SECONDS);
    executor.shutdown();
    
    // Assert checkpoint exists
    assertNotNull("Expecting the initial checkpoint", indexUpdate.getCheckpoint());
    
    // Close
    indexUpdate.closeAndWait();
    
    // Assert cleanup
    assertNull("Checkpoint should be null after cleanup", indexUpdate.getCheckpoint());
}
```

### Incorrect example (pitfall: missing the "no changes" scenario):

```java
// ❌ Only tests when index changes occur — misses the resource leak on the no-changes path
public void cpCleanupWithChanges() throws Exception {
    addSomeContentToNodeStore();
    indexUpdate.run();
    indexUpdate.closeAndWait();
    // Only asserts the index ran, but doesn't assert checkpoint lifecycle
}
```