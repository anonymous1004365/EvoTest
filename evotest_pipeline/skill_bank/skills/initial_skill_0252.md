---
name: checkpoint-abort-concurrent-task-state
description: WHEN the TG encounters code that orchestrates distributed checkpoint
  triggers with pending task references (like ExecutionVertex[] tasksToTrigger and
  a shared pending checkpoint state), THEN it should test concurrent scenarios where
  trigger tasks finish before the coordinator starts, to catch race conditions where
  finished tasks are not checked before checkpoint initiation.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- CONCURRENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# checkpoint-abort-concurrent-task-state

## Instructions

# Checkpoint Abort on Concurrent Task State

## Instructions

- WHEN the TG encounters `CheckpointCoordinator` code that:
  - Maintains an array/set of `ExecutionVertex` tasks to trigger (`tasksToTrigger`)
  - Maintains a collection of pending checkpoint instances (`pendingCheckpoints`)
  - Has a `triggerCheckpoint()` or similar method that iterates over tasks to trigger and initiates checkpoint operations
  - Has separate logic to handle task completion/failure (e.g., `taskFinished()` or `abortPendingCheckpoints()`)

- THEN the TG should write a test that:
  - Simulates a scenario where **all trigger tasks complete (finish) before `triggerCheckpoint()` is called**
  - Verifies that the coordinator **aborts** the checkpoint when it detects that all tasks are already finished (i.e., no tasks remain to be triggered)
  - Checks that no checkpoint is started (no pending checkpoint is registered) when all trigger tasks are done
  - Specifically verifies that `triggerCheckpoint()` returns `false` or the checkpoint is properly aborted with an appropriate exception/message

- **Common pitfalls** (what the TG might do wrong without this skill):
  - Testing only the "happy path" where tasks are running and available when a checkpoint is triggered
  - Failing to test the edge case where concurrent task completion happens before the checkpoint operation begins
  - Assuming that a checkpoint will always be successfully started when `triggerCheckpoint()` is called
  - Testing only single-threaded sequential scenarios without considering concurrent task state transitions

- **Correct test approach** (example):
```java
// 1. Create tasks that complete immediately
// 2. Ensure all tasks are in finished state
// 3. Call triggerCheckpoint()
// 4. Assert the checkpoint was NOT created (no pending checkpoint)
// 5. Assert triggerCheckpoint() returned false or appropriate status
```

- **Incorrect test approach** (what to avoid):
```java
// ❌ BAD: Only tests the normal case where tasks are available
// Does not test what happens when tasks finish before the trigger
```