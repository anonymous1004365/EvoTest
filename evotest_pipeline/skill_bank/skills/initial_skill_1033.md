---
name: execution-graph-archived-state-after-restart
description: Detects when ExecutionGraph transitions to a terminal state during restart
  sequence and fails to archive the job, leaving it as FAILED instead of FINISHED.
  Use when testing execution graph lifecycle after job completion.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
- NULL_CHECK
- CONCURRENCY
test_pattern: STATE_TEST
---

# execution-graph-archived-state-after-restart

## Instructions

# Execution Graph Archived State After Restart

## Instructions

- WHEN the TG encounters an `ExecutionGraph` that has a restart strategy configured (e.g., `FixedDelayRestartStrategy`) and the test verifies behavior after all task executions complete successfully following a restart:
  - THEN the TG should verify that the `ExecutionGraph` transitions through the correct job state sequence (RUNNING -> FAILING -> RESTARTING -> RUNNING -> FINISHED), and that the final job state is `JobStatus.FINISHED` (not `JobStatus.FAILED`)
  - The test must simulate a complete execution lifecycle: (1) create an `ExecutionGraph` with a restart strategy (e.g., `new FixedDelayRestartStrategy(1, 0L)`), (2) schedule and run the graph, (3) trigger a vertex failure via `vertex.fail(new Exception(...))`, (4) complete the restart by calling `restartAfterFailure(eg, ...)` or similar, (5) transition all vertices to RUNNING then FINISHED, (6) assert that `eg.getState()` equals `JobStatus.FINISHED`
  - A key pitfall to avoid: asserting that the job reaches FINISHED after restart without ensuring that the `ExecutionGraph.archive()` mechanism runs and properly archives the job. On the buggy version, if the execution graph enters a FAILED state during the restart sequence (e.g., because a vertex failure arrives after the graph has already been marked as globally modified), it can remain stuck in FAILED even after all vertices finish, because the `archive()` method may check the job state too early and never transition to FINISHED.

- WHEN testing execution vertex transitions through multiple lifecycle attempts on an `ExecutionGraph` with a restart strategy:
  - THEN the TG should verify the `ExecutionState` of each `ExecutionVertex` through the sequence: CREATED -> SCHEDULED -> DEPLOYING -> RUNNING -> FAILED (first attempt) -> CREATED (after restart) -> SCHEDULED -> DEPLOYING -> RUNNING -> FINISHED
  - Use `vertex.getCurrentExecutionAttempt().getState()` to assert state transitions per attempt
  - A common mistake is only asserting the final job-level state (`JobStatus`) without verifying per-vertex execution attempt states, which can mask a failure where some vertex executions never properly transition to FINISHED

- WHEN the test involves concurrent vertex failures (multiple `ExecutionVertex` instances failing around the same time) on an `ExecutionGraph`:
  - THEN the TG should use latches or countdown latches to synchronize the failure and completion events, ensuring the test sequence is deterministic
  - For example, use a `CountDownLatch` to wait until the job enters `RESTARTING` state before finishing the cancellation of all failed vertices
  - A common pitfall is not properly synchronizing the restart sequence, causing race conditions where the test assertion checks job state before all vertex state transitions have completed