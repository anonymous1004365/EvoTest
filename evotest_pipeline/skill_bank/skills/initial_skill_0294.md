---
name: cancel-task-exception-handling
description: When a task execution catches a CancelTaskException during the invoke()
  call, the execution state must transition to CANCELED, not FAILED. This skill helps
  tests verify that task cancellation exceptions are handled correctly and do not
  corrupt the task state.
code_tags:
- EXCEPTION_HANDLING
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# cancel-task-exception-handling

## Instructions

# CancelTaskException Handling in Task Execution

## Instructions

**WHEN** the TG encounters code where a `CancelTaskException` is thrown during task execution (e.g., inside an `AbstractInvokable.invoke()` method), and the task framework catches this exception in a `catch (Throwable t)` or `catch (Exception e)` block that also handles other failures:

- **THEN** the TG should write a test that verifies the task's final `ExecutionState` is `CANCELED` (not `FAILED`) when a `CancelTaskException` is thrown inside `invoke()`.
- The test should create a custom `AbstractInvokable` subclass whose `invoke()` method throws a `CancelTaskException` directly.
- The test should execute the `Task.run()` method and then assert that `task.getExecutionState()` equals `ExecutionState.CANCELED`.
- The test should also verify that `task.isCanceledOrFailed()` returns `false` — wait, verify that `task.getExecutionState()` is `CANCELED`.
- Additionally, verify that no `FAILED` state transition message was sent to the job manager (the task should not be treated as a failure).

**Common pitfalls:**
- Do NOT test that the task state becomes `FAILED` — `CancelTaskException` is not a failure, it is a controlled cancellation signal.
- Do NOT catch `CancelTaskException` separately for the test — the test should let it propagate naturally through the task's `run()` method.
- Do NOT forget to call `task.run()` synchronously in the test (not start a thread) so the state transitions happen deterministically.
- Do NOT override `cancel()` in the test invokable — the bug is about `CancelTaskException` thrown from `invoke()`, not from `cancel()`.
- Do NOT test with both cancellation and failure simultaneously — test the clean `CancelTaskException` path in isolation first.

**Correct example (Java):**
```java
public class InvokableWithCancelTaskExceptionInInvoke extends AbstractInvokable {
    @Override
    public void invoke() {
        throw new CancelTaskException();
    }
}

@Test
public void testCancelTaskException() throws Exception {
    final Task task = createTask(InvokableWithCancelTaskExceptionInInvoke.class);
    task.registerExecutionListener(mockListener);
    task.run();
    assertEquals(ExecutionState.CANCELED, task.getExecutionState());
}
```

**Incorrect example (would pass on buggy code but fail on fixed):**
```java
// WRONG: Asserts FAILED instead of CANCELED
@Test
public void testBadCancelTaskException() throws Exception {
    final Task task = createTask(InvokableWithCancelTaskExceptionInInvoke.class);
    task.run();
    assertEquals(ExecutionState.FAILED, task.getExecutionState()); // BUG: should be CANCELED
}
```