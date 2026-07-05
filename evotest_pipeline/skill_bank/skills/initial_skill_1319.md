---
name: concurrent-index-conflict-detection
description: When testing async index update operations under concurrent write scenarios,
  ensure that commit conflicts (e.g., conflicting writes detected by a commit hook)
  are properly detected and trigger a failure/retry rather than being silently overwritten.
  This applies to AsyncIndexUpdate-like code that processes queue-based index changes.
code_tags:
- CONCURRENCY
- STATE_MUTATION
- CONFLICT_DETECTION_MISSING
test_pattern: STATE_TEST
---

# concurrent-index-conflict-detection

## Instructions

# Concurrent Index Update Conflict Detection

## Instructions

- WHEN the TG encounters an async index update class (e.g., `AsyncIndexUpdate`) that processes index changes from a queue and commits them to a repository (e.g., a `NodeStore` or `ContentRepository`)
- THEN the TG should test that when a **commit conflict** occurs (e.g., conflicting concurrent writes that cause a `CommitFailedException` with `ConstraintViolation` type, or a conflict marker in the commit hook), the index update **fails with a visible error/exception** instead of silently proceeding or overwriting the conflict.

- Specifically:
  - WHEN the TG tests an `asyncIndexUpdate.run()` or similar method that processes a batch of changes and commits them
  - THEN the TG should **first apply changes directly** (e.g., via a separate session/thread) to create a conflicting state before the async index update runs
  - THEN after running the async index update, the TG should **verify that the conflict marker is detected**, typically by checking that a subsequent operation fails or that the repository state has not been corrupted
  - THEN the TG should also verify that after the failed run, the system does **not** leave dangling/inconsistent state (e.g., no leftover conflict markers)

- Common pitfalls to avoid:
  - ❌ Testing only the happy path where no concurrent modifications occur — this misses the entire conflict scenario
  - ❌ Silently catching `CommitFailedException` in the production code without rethrowing or recording the error — the test must verify this does NOT happen
  - ❌ Testing with only a single session/thread — the bug requires concurrent modifications from **different** sessions to trigger
  - ❌ Assuming the async index update always succeeds — the test must prove it **fails on conflict**
  - ❌ Not verifying the *state* after the conflict — the test should check that the conflicting writer's changes are preserved and the index update's changes are rejected

- Example of correct test approach:
  ```java
  @Test
  public void failOnConflict() throws Exception {
      // Setup: start with an empty repository and async index update
      NodeStore store = createNodeStore();
      AsyncIndexUpdate async = new AsyncIndexUpdate(store);
      
      // First session modifies the node (simulating another concurrent writer)
      ContentSession session1 = store.login(new AnonymousCredentials());
      NodeState root1 = session1.getRoot();
      // ... apply changes that conflict with what the index update will do
      root1.getChildNode(":async").getChildNode("update").getProperty("start");
      // ... commit session1's changes
      
      // Async index update attempts to process its queue
      async.run();  // This should FAIL due to conflict
      
      // After the failure, the conflicting state should be preserved
      ContentSession session2 = store.login(new AnonymousCredentials());
      NodeState root2 = session2.getRoot();
      assertFalse("conflict marker detected", 
          root2.hasChildNode(":conflict"));
  }
  ```

- Example of incorrect test approach (missing the bug):
  ```java
  @Test
  public void testAsyncIndexUpdate_success() throws Exception {
      // Only tests the happy path — no concurrent modifications
      AsyncIndexUpdate async = new AsyncIndexUpdate(store);
      async.run();
      // Asserts success without ever creating a conflict
      assertTrue(indexUpdatedCorrectly());
  }
  ```