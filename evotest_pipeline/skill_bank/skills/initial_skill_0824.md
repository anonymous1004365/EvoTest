---
name: concurrent-state-transition-race-condition
description: When testing code with state machines that have concurrent transitions
  (e.g., cancel, fail, restart), verify that intermediate states are properly captured
  before state changes via assertions on the final state. This skill helps catch bugs
  where a state transition overwrites another concurrent transition's expected intermediate
  state.
code_tags:
- STATE_MUTATION
- CONCURRENCY
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# concurrent-state-transition-race-condition

## Instructions

# Concurrent State Transition Race Condition

## Instructions

WHEN the TG encounters code that manages a state machine with transitions like `CANCEL`, `FAIL`, or `RESTART` that can be triggered concurrently (e.g., from different threads), it should:

1. **Identify if the state mutation can be overwritten by a concurrent transition.** Check if the code has a sequence like:
   - Transition to intermediate state (e.g., `FAILING`)
   - Perform operation on the intermediate state (e.g., `fail()`)
   - Another thread calls a different transition (e.g., `cancel()`)
   - The second transition checks the current state but may overwrite the state before the first transition completes its mutation

2. **Create a test that exercises the overlapping lifecycle sequence:**
   - Start the first async operation that transitions to an intermediate state (e.g., use `suspend` or a mock `Executor` to delay completion)
   - While the first operation is in its intermediate state, trigger the second operation from a different thread
   - Assert that the final state is the **expected result of the concurrent interaction**, not an incorrect stale state
   - For example, in an ExecutionGraph: trigger `fail()` (which sets `FAILING`), then while still failing, trigger `cancel()` — the final state should be `CANCELLING`, not `FAILING`, because cancel should have been respected

3. **Use real concurrent execution patterns**, not just sequential mocking:
   - Use `ExecutorService` with `submit()` and `CountDownLatch` to synchronize the timing
   - Use the same `Executor` that the production code uses (or a controlled `ScheduledExecutorService`)
   - Wait for the first transition to reach its intermediate state before triggering the second

4. **Assert on the final state after both operations complete**, using `assertThat(graph.getState(), is(ExecutionState.CANCELLING))` (or the expected correct final state).

5. **Common pitfalls to avoid:**
   - ❌ Testing only sequential transitions without overlapping timing
   - ❌ Using mocks that don't simulate the actual async execution behavior
   - ❌ Not waiting for the first transition to actually reach its intermediate state before firing the second
   - ❌ Only asserting the state immediately after the second trigger, without waiting for completion
   - ❌ Testing cancel-then-fail but missing the fail-then-cancel case

6. **Concrete example of the pattern tested in ExecutionGraphRestartTest.testCancelWhileFailing:**
   - Use `ScheduledExecutorService` with `submit()` that returns a `CompletableFuture`
   - The `fail()` call triggers failure transitioning tasks to `FAILING`
   - Use a latch to ensure `cancel()` is called while tasks are still in the `FAILING` transition
   - After the cancel, verify the execution state becomes `CANCELLING` (not stuck at `FAILING`)
   - Wait for all async operations to complete, then verify final state

7. **If the code handles a state enum like `ExecutionState`**, check every `transitionState()` or setter call to see if it properly checks the current state before overwriting it. If the code uses `compareAndSet(expect, update)`, test the race where `expect` is outdated due to a concurrent transition.