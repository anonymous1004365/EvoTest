---
name: shutdown-once-flag-validation
description: When a service manages a shutdown flag (e.g., isShutdown()) to prevent
  double-shutdown, test that the flag is set before the shutdown logic executes —
  not after — so re-entrant calls are properly guarded. Use for any ServiceSupport
  or lifecycle-aware endpoint that tracks shutdown state.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# shutdown-once-flag-validation

## Instructions

# Shutdown-Once Flag Validation

## Instructions

- WHEN the TG encounters a class that extends `ServiceSupport` (or implements `Service`) and overrides lifecycle methods (`doStart`, `doStop`, `doShutdown`), AND the class tracks a shutdown/stopped state (e.g., a `shutdown` boolean field or an `isShutdown()` check)
- THEN the TG should write a test that:
  1. Creates an instance of the endpoint/service
  2. Calls `start()` on it (to transition to "Started" state)
  3. Calls the lifecycle method TWICE (e.g., `shutdown()` or `stop()`) in succession
  4. Asserts that the second call does NOT throw an exception and does NOT re-execute the shutdown logic (e.g., no double-close of resources, no NullPointerException when accessing already-nullified fields)
- The test should specifically verify the ordering: the `shutdown` flag must be set to `true` **before** the shutdown logic body executes (e.g., before nullifying references or closing resources). If the flag is set **after** the body, the second call will re-execute the body, causing errors.
- Common pitfalls:
  - Testing only the first shutdown call (which always works)
  - Writing a unit test that mocks the service instead of testing the real lifecycle
  - Checking the flag value but not verifying that the second call's body is actually skipped
  - Assuming `stop()` and `shutdown()` have the same guard logic — they may not; test both separately

### Correct test pattern (Java/JUnit 4):
```java
@Test
public void testShutdownOnce() throws Exception {
    MyEndpoint endpoint = new MyEndpoint(...);
    endpoint.start();  // transition to Started state
    endpoint.shutdown();  // first call — should succeed
    endpoint.shutdown();  // second call — must NOT throw or NPE
}
```

### Common mistake (wrong pattern):
```java
@Test
public void testShutdownOnce() {
    MyEndpoint endpoint = new MyEndpoint(...);
    endpoint.shutdown();  // only one call — misses re-entrant bug
    // No second call to verify the guard flag works
}
```