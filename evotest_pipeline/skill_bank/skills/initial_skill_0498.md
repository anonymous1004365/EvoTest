---
name: asynchronous-index-update-checkpoint-consistency
description: When testing async index update lifecycle with checkpoint creation, the
  TG should verify that after a crash or restart, the index update can still access
  a valid root builder from the checkpoint. This skill catches bugs where the root
  builder obtained after a checkpoint is lost or invalid.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# asynchronous-index-update-checkpoint-consistency

## Instructions

# Asynchronous Index Update Checkpoint Consistency

## Instructions

- WHEN the TG encounters an asynchronous index update process that involves creating a checkpoint (via `checkpoint(long)` or similar) on a `NodeStore`, and then later using that checkpoint (via `store.getRoot().builder()` or `after.builder()`) to perform index updates,
- THEN the TG should write a test that:
  1. Creates a checkpoint on the store and obtains a root `NodeState`.
  2. Retrieves a `NodeBuilder` from that root state (e.g., `after.builder()`).
  3. Verifies that the builder is valid and can be used to make modifications (e.g., setting a property).
  4. Verifies that changes made through the builder can be merged back into the store.
  5. Tests that a second checkpoint obtained in a subsequent "run" (simulating a crash + restart scenario) produces a valid root/builder as well.

- The triggering test `branchBaseOnCheckpoint` exposed a bug where after a restart (simulated by a second `run()` with a new checkpoint), `store.getRoot().builder()` returned a `NodeBuilder` that was no longer connected to the store, causing a silent failure where index updates were lost. The test should explicitly assert that properties set through the builder persist after merge.

- **Common pitfalls to avoid:**
  - Testing only the first checkpoint without simulating a restart/crash cycle.
  - Assuming that `after.builder()` always returns a valid, writable `NodeBuilder` connected to the underlying store.
  - Not asserting that the merged changes (e.g., a property set on the builder) are actually visible in the store afterward.

- **Correct example (Java, JUnit):**
  ```java
  @Test
  public void branchBaseOnCheckpoint() throws Exception {
      // First run: create checkpoint, simulate index update
      NodeStore store = // obtain store
      String cp = store.checkpoint(Long.MAX_VALUE);
      NodeState after = store.retrieve(cp);
      NodeBuilder builder = after.builder();
      builder.setProperty("testKey", "testValue");
      builder.getNodeState(); // verify builder is usable
      store.close();

      // Second run: simulate restart, create new checkpoint
      store = // re-obtain store
      cp = store.checkpoint(Long.MAX_VALUE);
      after = store.retrieve(cp);
      builder = after.builder();
      builder.setProperty("testKey2", "testValue2");
      // Merge and assert
      NodeState merged = store.merge(builder, new EmptyHook(), CommitInfo.EMPTY);
      assertNotNull("merge should succeed", merged);
      assertEquals("testValue2", store.getRoot().getProperty("testKey2").getValue().getString());
  }
  ```

- **Incorrect example (missing the restart simulation):**
  ```java
  @Test
  public void branchBaseOnCheckpoint() throws Exception {
      NodeStore store = // obtain store
      String cp = store.checkpoint(Long.MAX_VALUE);
      NodeState after = store.retrieve(cp);
      NodeBuilder builder = after.builder();
      builder.setProperty("testKey", "testValue");
      // Missing: second run to verify checkpoint consistency after restart
      // This would NOT catch the bug because only a single run was tested
  }
  ```