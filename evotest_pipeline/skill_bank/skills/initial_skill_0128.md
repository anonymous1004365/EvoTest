---
name: async-throttler-jmx-consistency
description: When a Throttler uses asyncDelayed=true and processes messages asynchronously,
  the JMX-reported MaximumRequestsPerPeriod may be stale during concurrent access.
  Tests should verify that JMX attribute values (like ExchangesCompleted, MaximumRequestsPerPeriod)
  are consistent after async message processing completes.
code_tags:
- CONCURRENCY
- STATE_MUTATION
- COUNT_MISMATCH_FIXED_MILLISECONDS
test_pattern: STATE_TEST
---

# async-throttler-jmx-consistency

## Instructions

# Async Throttler JMX Consistency Under Concurrency

## Instructions

- WHEN the TG encounters a `Throttler` configured with `asyncDelayed()` and used with a `seda:` endpoint (asynchronous processing) where the throttler's JMX `MaximumRequestsPerPeriod` attribute is read via `MBeanServer.getAttribute(throttlerName, "MaximumRequestsPerPeriod")` AFTER messages have been processed asynchronously:

  - THEN the TG should verify that the JMX-reported `MaximumRequestsPerPeriod` value matches the expected `throttleRate` (e.g., `10` for `throttle(10).timePeriodMillis(250)`) by making a synchronous `getAttribute(throttlerName, "MaximumRequestsPerPeriod")` call.

  - The TG should wait for all async messages to be fully received at the mock endpoint (`assertMockEndpointsSatisfied()`) and also use a `NotifyBuilder` to wait for a certain number of received exchanges (e.g., `whenReceived(5)`) to ensure the async processing has progressed sufficiently before reading JMX attributes.

  - The TG must NOT assume that async processing completes before the JMX attribute read — the test must use explicit synchronization (e.g., `NotifyBuilder.matches(timeout, TimeUnit)`) before reading the `MaximumRequestsPerPeriod` attribute.

  - The TG should verify `ExchangesCompleted` attribute (via `mbeanServer.getAttribute(routeName, "ExchangesCompleted")`) along with `MaximumRequestsPerPeriod` to ensure full consistency after async processing.

- Common pitfalls to avoid:
  - ❌ Reading JMX attributes immediately after sending messages to a `seda:` endpoint without waiting for async processing to finish — this can read stale/wrong values.
  - ❌ Only verifying mock endpoint message counts without verifying JMX attribute consistency.
  - ❌ Using `sync` throttling tests when the code under test uses `asyncDelayed()` — the async path has different timing and concurrency behavior.

- Correct example (after fix):
  ```java
  // Setup route with async throttler
  from("seda:throttleCountAsync")
      .throttle(10).timePeriodMillis(250).asyncDelayed()
      .to("mock:endAsync");

  getMockEndpoint("mock:endAsync").expectedMessageCount(10);
  NotifyBuilder notifier = new NotifyBuilder(context)
      .from("seda:throttleCountAsync").whenReceived(5).create();

  for (int i = 0; i < 10; i++) {
      template.sendBody("seda:throttleCountAsync", "Message " + i);
  }
  assertTrue(notifier.matches(2, TimeUnit.SECONDS));
  assertMockEndpointsSatisfied();

  Long completed = (Long) mbeanServer.getAttribute(routeName, "ExchangesCompleted");
  assertEquals(10, completed.longValue());
  ```

- Incorrect example (before fix — would fail):
  ```java
  getMockEndpoint("mock:end").expectedMessageCount(10);
  for (int i = 0; i < 10; i++) {
      template.sendBody("seda:throttleCount", "Message " + i);
  }
  // Missing NotifyBuilder wait — may read stale ExchangesCompleted value
  assertMockEndpointsSatisfied();
  Long completed = (Long) mbeanServer.getAttribute(routeName, "ExchangesCompleted");
  assertEquals("expected:<10> but was:<9>", 10, completed.longValue()); // FAILS
  ```