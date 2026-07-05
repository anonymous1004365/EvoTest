---
name: cancel-fail-race-condition
description: When a job is being CANCELED and then a failure is triggered simultaneously,
  the state transition must respect the CANCELED state. This skill teaches how to
  test for race conditions where cancel and fail operations interleave and the job
  should remain CANCELED rather than transitioning to RESTARTING.
code_tags:
- CONCURRENCY
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# cancel-fail-race-condition

## Instructions

# Cancel and Fail Race Condition

## Instructions

- WHEN the TG encounters a `ExecutionGraph` or similar job execution manager that has both a `cancel()` (or suspend/stop) method and a failure-handling method (e.g., `failGlobal`, `failJob`, `handleFailure`) that can change the job's `JobStatus`, AND these methods are called concurrently or in rapid succession from different threads:
  - THEN the TG should write a test that:
    1. Starts a job execution (e.g., submitting a job and waiting until it reaches `JobStatus.RUNNING`)
    2. Calls `cancel()` on the execution graph (or equivalent cancel operation)
    3. While the cancel is still in flight or immediately after, triggers a failure on the same execution graph (e.g., via `failGlobal(new Throwable(...))`)
    4. Asserts that the final job status is `JobStatus.CANCELED`, NOT `JobStatus.RESTARTING` or `JobStatus.FAILED`
  - The test must verify that the CANCELED state is the terminal state and is not overwritten by a concurrent failure that attempts to trigger a restart.

- WHEN the TG sees that the job's status is managed by an `AtomicReferenceFieldUpdater` (e.g., `STATE_UPDATER`) or `AtomicReference`:
  - THEN the TG should recognize that the code is using lock-free state transitions and that race conditions between status-changing operations are possible
  - The test should not rely on sleeps or timeouts but instead cause the concurrent operations genuinely (e.g., by calling methods from different threads or using an executor service with a `CountDownLatch` to orchestrate the interleaving)
  - The test should check the final status after both operations have completed

- WHEN the TG writes a test for this race condition:
  - THEN the TG must use `waitUntilJobStatus(eg, JobStatus.RUNNING)` (or the appropriate wait utility) to synchronize before triggering the race
  - The TG must verify the status is `JobStatus.CANCELED` using `assertEquals(JobStatus.CANCELED, eg.getState())` — this assertion should fail on the buggy version because the concurrent failure incorrectly transitions from CANCELED to RESTARTING

- Common pitfalls to avoid:
  - ❌ Testing only sequential cancel-then-fail (no concurrency) — this does NOT trigger the bug; the bug requires interleaved execution
  - ❌ Using `Thread.sleep()` to simulate timing instead of orchestrating actual concurrent calls
  - ❌ Failing to wait for the job to reach RUNNING before initiating the cancel
  - ❌ Asserting only that no exception is thrown rather than checking the final state
  - ❌ Assuming that once `cancel()` returns, all state transitions are complete — the cancel may still be processing

### Example (Correct)

```java
@Test
public void testFailExecutionAfterCancel() throws Exception {
    final ExecutionGraph eg = createAndStartExecutionGraph();

    // Wait for job to be running
    waitUntilJobStatus(eg, JobStatus.RUNNING);

    // Initiate cancel
    eg.cancel();

    // While cancel is in progress (or immediately after), trigger a failure
    // This simulates the race condition where a failure handler fires concurrently
    eg.failGlobal(new Throwable("test failure"));

    // The final status should be CANCELED, not RESTARTING
    // On the buggy version, the failure overwrites CANCELED -> RESTARTING
    assertEquals(JobStatus.CANCELED, eg.getState());
}
```

### Example (Incorrect)

```java
@Test
public void testCancelThenFail_sequentialOnly() throws Exception {
    final ExecutionGraph eg = createAndStartExecutionGraph();
    waitUntilJobStatus(eg, JobStatus.RUNNING);
    
    eg.cancel();
    Thread.sleep(1000);  // ❌ Sleep-based timing
    assertEquals(JobStatus.CANCELED, eg.getState());
    
    eg.failGlobal(new Throwable("test"));
    // ❌ Only checks no exception — never verifies final state after both operations
    // ❌ The cancel and fail are sequential, not concurrent
}
```