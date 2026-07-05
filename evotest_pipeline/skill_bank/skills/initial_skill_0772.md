---
name: circuit-breaker-half-open-state-transition
description: When testing circuit breaker state transitions from HALF_OPEN to OPEN/CLOSED,
  the failures counter may not be properly reset or checked on each transition, causing
  unexpected message delivery. This skill helps write tests that verify correct half-open
  behavior after timeout.
code_tags:
- STATE_MUTATION
- CONCURRENCY
- CIRCUIT_BREAKER_STATE_TRANSITION
test_pattern: STATE_TEST
---

# circuit-breaker-half-open-state-transition

## Instructions

# Circuit Breaker Half-Open State Transition Verification

## Instructions

WHEN the TG encounters a CircuitBreakerLoadBalancer or similar circuit breaker implementation that uses `state`, `failures`, and `lastFailure` as shared mutable state (via AtomicInteger and long fields), and transitions between CLOSED, OPEN, and HALF_OPEN states:

- THEN the TG should write a test that:
  1. FIRST: Sends enough messages to exceed the threshold (e.g., threshold=2, send 2 failure-triggering messages) to force the circuit OPEN, then verify subsequent messages are rejected (e.g., get `RejectedExecutionException`)
  2. SECOND: After waiting for the half-open timeout period (e.g., `Thread.sleep(1000)` for `halfOpenAfter=1000L`), send additional messages to verify the circuit transitions to HALF_OPEN and allows exactly ONE test message through (the half-open probe), while subsequent messages are rejected if the probe also fails
  3. THIRD: Verify that when the half-open probe fails, the count of messages that pass through (the `mock:result` endpoint) matches the expected failed-probe behavior — e.g., only 1 message gets through in the half-open state, not 2 or 3

- When verifying half-open behavior with a continuously failing service:
  - Set up the mock endpoint to throw an exception (e.g., `MyCustomException`) on every exchange received via `whenAnyExchangeReceived`
  - After the open circuit timeout, send messages and assert that ONLY the first message reaches the mock endpoint (the half-open probe), and subsequent messages are rejected
  - The mock endpoint should expect exactly the right count: e.g., `expectsMessageCount(1, result)` for the half-open phase where the probe fails

- MUST test that the `failures` counter is properly reset or checked during state transitions:
  - When in HALF_OPEN state, the circuit should check if `failures.get() == 0` to decide whether to close (allow through) or open (reject)
  - A buggy implementation might allow messages through in HALF_OPEN even when failures > 0, causing more than expected messages to reach the processor

- Common pitfalls to avoid:
  - Testing only the CLOSED→OPEN transition without testing the OPEN→HALF_OPEN→re-OPEN sequence
  - Assuming that after timeout the circuit becomes fully closed again — it enters HALF_OPEN, not CLOSED
  - Not resetting the mock endpoint between phases (using `result.reset()` before setting new expectations)
  - Not accounting for async processing — test both sync (`direct:start`) and async (`direct:start-async` with `threads(1)`) endpoint variants

**Correct test example** (for half-open after timeout, service still failing):
```java
public void testHalfOpenAfterTimeout() throws Exception {
    expectsMessageCount(2, result);
    result.whenAnyExchangeReceived(exchange -> {
        exchange.setException(new MyCustomException());
    });
    
    // Phase 1: Send 2 failures to open circuit, then 2 more that get rejected
    sendMessage("message one");
    sendMessage("message two");
    sendMessage("message three");  // RejectedExecutionException
    sendMessage("message four");   // RejectedExecutionException
    assertMockEndpointsSatisfied();  // Only 2 reached mock:result
    
    // Wait for half-open timeout
    Thread.sleep(1000);
    result.reset();
    result.whenAnyExchangeReceived(exchange -> {
        exchange.setException(new MyCustomException());
    });
    expectsMessageCount(1, result);
    
    // Phase 2: First message enters half-open (probe), second is rejected
    sendMessage("message five");   // Gets through (half-open probe)
    sendMessage("message six");    // Rejected (failures still > 0)
    assertMockEndpointsSatisfied();  // Only 1 reached mock:result
    
    // Verify exception types
    assertTrue(exchangeFive.getException() instanceof MyCustomException);
    assertTrue(exchangeSix.getException() instanceof RejectedExecutionException);
}
```

**Incorrect test example** (missing phase separation, no mock reset):
```java
// WRONG: No mock endpoint reset between phases
// WRONG: Not expecting exactly 1 message in half-open phase
// WRONG: Not checking which specific exchanges get through
public void testHalfOpenBad() throws Exception {
    expectsMessageCount(3, result);  // Wrong count — should be 2 then 1
    // ... sends messages without proper phase management
}
```