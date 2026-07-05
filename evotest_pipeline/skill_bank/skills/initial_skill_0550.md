---
name: throttler-jmx-state-synchronization
description: When a Throttler's maximum requests per period is changed programmatically,
  the getCurrentMaximumRequestsPerPeriod() JMX method may not reflect the latest update
  due to asynchronous state handling. The TG should test that JMX-exposed state remains
  consistent after dynamic updates.
code_tags:
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# throttler-jmx-state-synchronization

## Instructions

# Throttler JMX State Synchronization

## Instructions

- WHEN the TG encounters a `Throttler` processor whose maximum requests per period can be changed dynamically via a setter (e.g., `setMaximumRequestsPerPeriod(int)`) and the current value is exposed through a separate method (e.g., `getCurrentMaximumRequestsPerPeriod()`) that may be called by a JMX `ManagedThrottler` MBean
- THEN the TG should write a test that:
  1. Creates a `Throttler` instance with an initial maximum requests per period (e.g., 10).
  2. Calls the setter to change the maximum requests per period to a new value (e.g., 1).
  3. Calls `getCurrentMaximumRequestsPerPeriod()` directly on the `Throttler` instance and verifies it returns the newly set value (expecting the updated value, not the stale initial one).
  4. If testing via JMX, also verify that `ManagedThrottler.getMaximumRequestsPerPeriod()` returns the updated value after the change.
- The test should expect the assertion to pass with the **fixed** code; on the **buggy** version, the TN will fail because `getCurrentMaximumRequestsPerPeriod()` does not immediately reflect the setter change (it returns the previous value because of asynchronous/deferred state calculation).
- Common pitfalls to avoid:
  - Testing only the setter/getter pair without involving the `getCurrentMaximumRequestsPerPeriod()` method, which is the actual source of truth used by JMX.
  - Assuming that `getMaximumRequestsPerPeriod()` (the simple field getter) and `getCurrentMaximumRequestsPerPeriod()` (which computes/delegates differently) are always in sync.
  - Not including a route that actually triggers `calculateAndSetMaxRequestsPerPeriod()` if the throttler's internal logic requires a `process()` call to recalculate state — however, the bug here is that the setter should immediately update the underlying state, so a direct test after the setter call suffices.

### Correct example (detects the bug):
```java
Throttler throttler = new Throttler(null, null, 10);
throttler.setMaximumRequestsPerPeriod(1);
assertEquals(1, throttler.getCurrentMaximumRequestsPerPeriod());
```

### Incorrect example (misses the bug):
```java
Throttler throttler = new Throttler(null, null, 10);
throttler.setMaximumRequestsPerPeriod(1);
assertEquals(1, throttler.getMaximumRequestsPerPeriod()); // Always passes, even on buggy version
```