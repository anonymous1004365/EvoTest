---
name: async-index-recover-from-missing-checkpoint
description: When the mergeWithConcurrencyCheck method is called with a potentially
  null checkpoint reference from NodeState, the TG should test that the code gracefully
  handles a missing checkpoint instead of causing a CommitFailedException.
code_tags:
- NULL_CHECK
- VALIDATION
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# async-index-recover-from-missing-checkpoint

## Instructions

# Async Index Recover From Missing Checkpoint Reference

## Instructions

- WHEN the TG encounters code in `AsyncIndexUpdate` where a `checkpoint` value is retrieved via `async.getString(name)` and then passed to `mergeWithConcurrencyCheck(builder, ...)`, 
- THEN it should verify that when the checkpoint string is `null` (e.g., because the `"async"` child node does not contain a value for that name), the method does **not** pass `null` to `Objects.equal(checkpoint, ...)` without a guard.
  - Specifically, the fix added a `checkpoint == null ||` guard before `Objects.equal(checkpoint, async.getString(name))`.
  - Write a test that creates a situation where the async node's property for the given name is missing or `null`, triggering the `null` checkpoint path.
  - The test should verify that the system can recover gracefully from a missing checkpoint reference (i.e., it does **not** throw `CommitFailedException` due to an unguarded `Objects.equal(null, ...)` call).
  - In the test, assert that the index update completes without exceptions and correctly transitions state.

- Common pitfalls:
  - Testing only with valid, non-null checkpoint values. The bug is specifically triggered when the checkpoint is `null`.
  - Assuming `Objects.equal(null, async.getString(name))` is safe — it is not if the first argument is the checkpoint that could be `null` and the second is also `null` in a way that bypasses the intended logic.
  - Forgetting to test the recovery scenario where `async.getString(name)` returns `null` and the code must decide to continue with a fresh checkpoint instead of failing.

- Example of a correct test:
```java
@Test
public void recoverFromMissingCpRef() throws Exception {
    // Setup: create an index update with no previous checkpoint
    // (so async.getString(name) returns null)
    // Then run the async index update and verify it completes
    // without throwing CommitFailedException
    executor.execute(index);
    executor.await();
    // Verify that no exception was thrown and state is correct
    assertTrue("Index update should have completed", ...);
}
```

- Example of an incorrect test:
```java
@Test
public void testMergeWithConcurrencyCheck() throws Exception {
    // Setup with a valid checkpoint string
    // This test will NOT catch the bug because the null case is never exercised
    executor.execute(index);
    // ...
    // The test passes on both buggy and fixed versions,
    // giving false confidence
}
```

- The TG should specifically ensure that `async.getString(name)` can return `null` in the test scenario, and that the code path through `mergeWithConcurrencyCheck` handles this without crashing.