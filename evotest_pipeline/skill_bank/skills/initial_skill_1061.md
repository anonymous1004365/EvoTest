---
name: savepoint-rollback-state-cleanup
description: When testing savepoint rollback logic, verify the rollback also properly
  reverts checkpoint/snapshot state in the backend (e.g., pending checkpoints map).
  Without proper cleanup, rollback leaves stale entries that can cause assertion failures
  or inconsistent state.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# savepoint-rollback-state-cleanup

## Instructions

# Savepoint Rollback Must Clean Up Backend State

## Instructions

- WHEN the TG encounters a `SavepointCoordinator` (or similar coordinator class) that has a `rollbackSavepoint(..)` or `rollback(..)` method
- THEN the TG should verify that after rollback, the associated state backend / checkpoint store is also rolled back/cleaned up — not just the coordinator-level savepoint reference.
- Specifically, check whether the test creates a savepoint via `coordinator.savepoint(..)` and then calls `coordinator.rollback(..)`. After rollback, verify that pending checkpoint state in the backend (e.g., entries in a `Map<Long, ? extends PendingCheckpoint>` or equivalent) are removed or reverted to their pre-savepoint state.
- Include assertions that check:
  1. After rollback, the savepoint is no longer present in the coordinator.
  2. After rollback, any checkpoint IDs/snapshots created as part of the savepoint are cleaned up from the state backend/checkpoint store.
  3. The test should catch scenarios where the coordinator's rollback returns `true` (success) but leftover state in the backend causes later assertions to fail.
- Common pitfalls:
  - Testing only that `rollbackSavepoint()` returns successfully without verifying backend state cleanup.
  - Only checking the coordinator's in-memory state (e.g., savepoint list) while ignoring the checkpoint storage backend.
  - Using a mock backend that silently accepts all operations without actually storing state — this masks cleanup bugs.
  - Assuming that because `rollbackSavepoint()` exists, it correctly cleans up all state — the bug is often that it only cleans up the reference but not the data.

### Correct Example (what the test should do)

```java
// Given: a savepoint is triggered
coordinator.savepoint(savepointPath);
// Assert: state backend has the pending checkpoint
assertFalse("Backend should have pending checkpoint after savepoint",
    checkpointStorage.getPendingCheckpoints().isEmpty());

// When: the savepoint is rolled back
coordinator.rollbackSavepoint(savepointPath);

// Then: both the coordinator reference and backend state are cleaned up
assertFalse("Coordinator should no longer list this savepoint",
    coordinator.getSavepoints().contains(savepointPath));
assertTrue("Backend should have no pending checkpoints after rollback",
    checkpointStorage.getPendingCheckpoints().isEmpty());
```

### Incorrect Example (the pitfall)

```java
// Given: a savepoint is triggered
coordinator.savepoint(savepointPath);

// When: rolled back
boolean result = coordinator.rollbackSavepoint(savepointPath);

// Then: only checks the return value and coordinator state — misses backend
assertTrue("Rollback should succeed", result);
assertFalse("Savepoint removed from coordinator", coordinator.hasSavepoint(savepointPath));
// BUG: pending checkpoint in backend is NOT cleaned up — test passes but leaves stale state!
```