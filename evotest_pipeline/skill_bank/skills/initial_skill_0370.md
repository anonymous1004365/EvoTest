---
name: throttler-rate-change-visibility
description: When testing managed throttler rate changes via JMX, validate that all
  subsequent exchanges observe the updated rate, not just a subset. This is critical
  for async/concurrent throttler scenarios where rate changes may not be immediately
  visible to all executing threads.
code_tags:
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# throttler-rate-change-visibility

## Instructions

# Throttler Rate Change Visibility Under Concurrency

## Instructions

- WHEN the TG encounters a `Throttler` (or `ManagedThrottler`) that allows rate changes via `setMaximumRequestsPerPeriod(long)` on a MBean, and messages are sent concurrently (e.g., via `seda:` endpoint) or asynchronously through the throttler:
  - THEN the TG should verify that after changing the throttle rate via JMX, all subsequently sent messages (not just some) respect the new rate. The test should send a batch of messages (e.g., 10), read the `ExchangesCompleted` count from the route MBean, and assert that exactly 10 messages were completed. The test must use a `NotifyBuilder` to wait until a certain number of messages have been received (e.g., 5) before asserting completion, because with `seda:` endpoints the messages may be processed asynchronously. A common failure is that `ExchangesCompleted` shows fewer messages than sent (e.g., 9 instead of 10) because there is a race condition between the async processing thread completing the exchange and the test thread reading the JMX attribute.

- WHEN the TG sees a throttler test that uses a `seda:` endpoint to send messages and a `ManagedThrottler` with `asyncDelayed=true` (e.g., `asyncDelayed=true` in the route):
  - THEN the TG should ensure the test uses `NotifyBuilder` with a `whenReceived(N)` condition on the correct `from("seda:...")` route, and calls `notifier.matches(2, TimeUnit.SECONDS)` to wait for enough messages to arrive before asserting JMX counters. Failing to wait properly can cause `ExchangesCompleted` to return a stale value (e.g., expected `<10>` but was `<9>`).

- Common pitfalls to avoid:
  - **Pitfall**: Reading JMX attributes (e.g., `ExchangesCompleted`) immediately after sending messages via a `seda:` endpoint, without waiting for async processing to complete. The test must wait for all messages to be fully processed, not just sent.
  - **Pitfall**: Not resetting the JMX counters via `mbeanServer.invoke(routeName, "reset", null, null)` before the batch under test, leading to stale counts from previous batches.
  - **Pitfall**: Assuming that setting `MaximumRequestsPerPeriod` via JMX `setAttribute` takes effect instantaneously for all in-flight async exchanges. Use `NotifyBuilder` to synchronize on receipt of a safe number of messages (e.g., halfway through the batch) before asserting.

### Correct approach example:
```java
// Reset counters before test batch
mbeanServer.invoke(routeName, "reset", null, null);

getMockEndpoint("mock:endAsync").expectedMessageCount(10);

// Wait until 5 messages have been received to avoid race conditions
NotifyBuilder notifier = new NotifyBuilder(context)
        .from("seda:throttleCountAsync").whenReceived(5).create();
for (int i = 0; i < 10; i++) {
    template.sendBody("seda:throttleCountAsync", "Message " + i);
}
assertTrue(notifier.matches(2, TimeUnit.SECONDS));
assertMockEndpointsSatisfied();

Long completed = (Long) mbeanServer.getAttribute(routeName, "ExchangesCompleted");
assertEquals(10, completed.longValue()); // <-- should be 10, not 9
```

### Incorrect approach (will fail):
```java
// BAD: No NotifyBuilder synchronization
getMockEndpoint("mock:endAsync").expectedMessageCount(10);
for (int i = 0; i < 10; i++) {
    template.sendBody("seda:throttleCountAsync", "Message " + i);
}
Long completed = (Long) mbeanServer.getAttribute(routeName, "ExchangesCompleted");
assertEquals(10, completed.longValue()); // <-- Race: may get 9
```