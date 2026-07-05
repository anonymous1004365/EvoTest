---
name: throttler-maximum-requests-concurrent-access
description: When a throttler's maximum requests per period is updated asynchronously,
  the getter may return a stale or intermediate value if not synchronized. Testers
  should verify that concurrent access to the maximum requests per period value produces
  consistent results under race conditions.
code_tags:
- CONCURRENCY
- STATE_MUTATION
test_pattern: STATE_TEST
---

# throttler-maximum-requests-concurrent-access

## Instructions

# Throttler Maximum Requests Per Period Concurrent Access

## Instructions

- WHEN the TG encounters a `Throttler` (or similar rate-limiter) class that exposes a `getCurrentMaximumRequestsPerPeriod()` method reading from a mutable field (`int` or `long`) that can be updated concurrently (e.g., via JMX, async JMX operations, or separate threads)
- THEN the TG should write a test that:
  1. Creates a `Throttler` instance (or a Camel route using a throttler) with an initial `maximumRequestsPerPeriod` value (e.g., 10)
  2. Modifies the throttler's maximum requests concurrently (e.g., via a JMX operation or direct setter call from another thread)
  3. Reads `getCurrentMaximumRequestsPerPeriod()` immediately after or during the concurrent modification
  4. Asserts that the observed value matches one of the expected values (the old value or the new value), but NOT an unexpected intermediate value like `0`, `-1`, or any garbage state
  5. Specifically assert that the value is always a positive integer within valid range, never unexpectedly reset to `0` or negative

- The test should verify that `getCurrentMaximumRequestsPerPeriod()` returns a valid positive value at all times, even when called concurrently with a setter that changes the value

- Common pitfalls to avoid:
  - Testing only in a single-threaded context (sequential set-then-get)
  - Forgetting that JMX or other async operations can race with the read
  - Assuming the getter returns the correct value without synchronization on the backing field
  - Not testing the case where the value is changed while another thread is actively reading it

- Example correct test structure:
  ```java
  // Create a throttler with initial max=10
  // Start a producer sending messages through the throttler
  // In a separate thread, update the maximum requests per period (e.g., to 5, 20, etc.)
  // In the main thread, repeatedly call getCurrentMaximumRequestsPerPeriod()
  // Assert that the returned value is always > 0 and is either the old or new max, never 0 or negative
  ```

- Example incorrect test (too weak):
  ```java
  // Sets max=10, reads getCurrentMaximumRequestsPerPeriod() once, gets 10 — passes but misses race condition
  // Does not perform concurrent updates while reading
  ```