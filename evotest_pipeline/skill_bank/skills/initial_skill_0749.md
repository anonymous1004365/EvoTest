---
name: concurrent-inflight-statistics-reset
description: WHEN encountering concurrent reads of inflight statistics counters that
  may be reset asynchronously, THEN test that statistics reads return consistent results
  (e.g., null vs. actual values) under concurrent reset operations. This helps catch
  race conditions where a value is read after being decremented before it is fully
  cleared.
code_tags:
- CONCURRENCY
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# concurrent-inflight-statistics-reset

## Instructions

# Concurrent Inflight Statistics Reset

## Instructions

WHEN the TG encounters a statistics/resource management class that maintains inflight counters (e.g., `exchangesInflight`, `oldestInflightDuration`, `minInflightDuration`, `maxInflightDuration`, `meanInflightDuration`) that:
1. Can be read via getter methods (e.g., `getExchangesInflight()`, `getOldestInflightDuration()`, etc.)
2. Can be reset (e.g., a `reset()` method that clears all counters)
3. Are updated concurrently (e.g., via increment/decrement operations on exchanges)

THEN the TG should write a **STATE_TEST** that:
1. Sets up a scenario where inflight statistics accumulate a known non-zero value (e.g., an exchange is started and completed)
2. Triggers a reset of the statistics (e.g., by calling `reset()`)
3. Concurrently (or in rapid succession) reads the statistics getter methods
4. Verifies that after the reset, the getter methods return consistent and correct values (e.g., `null` or `0`), not residual stale values from before the reset

**Specific verification to include:**
- After a route is stopped and started, the `getOldestInflightDuration()` and related duration methods should return `null` (not a previously set value like `1000`)
- The test should invoke the reset/stop logic and then immediately read the getters to catch race conditions

**Common pitfalls to avoid:**
- Testing only the happy path where statistics accumulate correctly but never verifying the reset behavior
- Assuming that after a reset, values are immediately consistent without verifying
- Testing inflight counters in isolation without triggering the concurrent reset path
- Forgetting to stop and restart the route to trigger the reset code path

**Correct example (from the triggering test):**
```java
// After route completes and is stopped/started
// getOldestInflightDuration() should return null
assertNull(route.getOldestInflightDuration());
// Other duration getters should also be null
assertNull(route.getMinInflightDuration());
assertNull(route.getMaxInflightDuration());
assertNull(route.getMeanInflightDuration());
```

**Incorrect approach:**
```java
// WRONG: Only testing the accumulated values, never the reset
assertNotNull(route.getOldestInflightDuration());  // Might pass but misses the reset bug
// Tests should verify both accumulation AND reset behavior
```