---
name: timer-consumer-cancel-on-suspend
description: WHEN a test pauses/resumes a Timer route or CamelContext with Suspension,
  THEN the test must verify that no timer events fire during the suspended period.
  Without this, consumers may keep firing because cancellation is missed or delayed.
code_tags:
- NULL_CHECK
- RESOURCE_MANAGEMENT
- TYPE_CONVERSION
test_pattern: STATE_TEST
---

# timer-consumer-cancel-on-suspend

## Instructions

# Timer Consumer Must Not Fire During Suspension

## Instructions

- WHEN a test suspends a Timer endpoint or a CamelContext containing a timer-based route, THEN the test MUST verify that the timer consumer is properly cancelled so that no exchange is produced during the suspension period.
- Specifically, after calling `context.suspend()` (or `consumer.suspend()`), the test MUST wait for any in-flight timer to complete, THEN assert that the mock endpoint received exactly 0 messages during the suspended interval.
- The test MUST use `mock.expectedMessageCount(0)` **before** the suspension, and `mock.assertIsSatisfied()` **during** or immediately after the suspension, to confirm no messages arrive while suspended.
- After `context.resume()`, the test MUST confirm that the timer re-fires as expected (at least 1 message) to verify the consumer properly restarted.
- Common pitfall: Calling `mock.expectedMessageCount(0)` but delaying the assertion too late, allowing a timer tick to slip through before the suspension takes effect. The timer's `ScheduledExecutorService` may schedule a task just before `doSuspend()` stops the consumer, and if the consumer's `doStop()` calls `future.cancel(false)` (not `true`), the running task is not interrupted.
- **Important**: The fix ensures that `doSuspend()` in the consumer properly cancels the scheduled future with `mayInterruptIfRunning=true`, or cancels before the task executes. The test must catch the case where a task fired during suspension.
- When writing the test, structure it as:
  1. Start route, let some messages flow (e.g. wait for 2+ ticks)
  2. Set expected count to 0 for the suspended interval
  3. Suspend context
  4. Wait long enough for at least one additional timer tick to be due
  5. Assert `mock.assertIsSatisfied()` — expects 0 during suspension
  6. Resume context
  7. Wait for at least one more tick
  8. Assert that messages arrive after resume (> 0)

### Correct Example (detects the bug):

```java
public void testTimerSuspendResume() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMinimumMessageCount(2);

    // Let some messages arrive before suspension
    mock.assertIsSatisfied();

    // Now suspend — expect NO messages during suspension
    mock.reset();
    mock.expectedMessageCount(0);
    context.suspend();

    // Wait long enough for a tick that would fire if consumer isn't cancelled
    Thread.sleep(300); // timer period is 100ms, so 3 ticks would fire

    mock.assertIsSatisfied(); // FAILS on buggy version: gets >0 messages

    // Resume and confirm it fires again
    context.resume();
    Thread.sleep(250);
    assertTrue(mock.getReceivedCounter() > 0);
}
```

### Incorrect Example (misses the bug):

```java
public void testTimerSuspendResume() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    context.suspend();
    // No assertion that 0 messages arrived during suspension
    Thread.sleep(500);
    context.resume();
    Thread.sleep(200);
    // Only checks that some messages arrived after resume — never catches
    // that messages arrived WHILE suspended
    assertTrue(mock.getReceivedCounter() > 0);
}
```