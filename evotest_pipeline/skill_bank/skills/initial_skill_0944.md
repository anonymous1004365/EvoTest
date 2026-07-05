---
name: aggregate-timeout-completion-cancellation
description: When a completion timeout fires but the exchange is silently discarded
  instead of being completed with the timeout result, the bug occurs because the timeout
  callback does not trigger the aggregation/completion logic. Use this skill to write
  tests that verify timed-out exchanges are properly completed, not lost.
code_tags:
- NULL_CHECK
- VALIDATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# aggregate-timeout-completion-cancellation

## Instructions

# Aggregate Timeout Completion Cancellation

## Instructions

- WHEN the TG encounters an `AggregateProcessor` (or similar aggregator) that uses `completionTimeout` combined with `completionSize` (or `completionPredicate`) and the timeout fires before the size/predicate condition is met
- THEN the TG should verify that when the timeout fires, the exchange is still aggregated/completed with the partial results received so far, rather than being silently discarded
- WHEN writing the test, create a route with:
  - An aggregator using `.completionTimeout(long)` (e.g., 500ms) and `.completionSize(int)` (e.g., 2)
  - Send only 1 message to the aggregator (fewer than the completion size)
  - Wait long enough for the timeout to fire (e.g., use `Thread.sleep(1000)` or a `MockEndpoint` with `await()`)
  - Assert that **the aggregated exchange IS received at the output endpoint** (e.g., using `MockEndpoint.getExchanges().size() == 1` or `assertIsSatisfied()`)
- WHEN testing the buggy version (pre-fix), the test should FAIL because the timed-out exchange is silently dropped instead of being completed
- WHEN testing the fixed version (post-fix), the test should PASS because the timeout callback triggers `onCompletion()` which aggregates and sends the partial result
- **Common pitfalls to avoid**:
  - Testing only the case where `completionSize` is met (this works in both buggy and fixed versions — the bug only manifests when timeout fires BEFORE size/predicate completes)
  - Not waiting long enough for the timeout to fire (use `MockEndpoint.await()` or sufficient sleep, accounting for scheduling jitter)
  - Assuming the timeout callback fires correctly without verifying the aggregation chain is invoked (the bug is that the callback fires but doesn't trigger `onCompletion`)
  - Using `completionTimeout` without also setting another completion condition like `completionSize` or `completionPredicate` — the bug specifically affects the interaction between timeout and other completion strategies

**Correct test approach:**
```java
public void testAggregateTimeout() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(1);
    
    template.sendBody("direct:start", "A");
    
    // Wait for timeout to fire - don't send second message
    Thread.sleep(2000);
    
    // The single message should still be completed and delivered on timeout
    assertMockEndpointsSatisfied();
}
```

**Incorrect test approach (does NOT catch the bug):**
```java
public void testAggregateSize() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(1);
    
    template.sendBody("direct:start", "A");
    template.sendBody("direct:start", "B"); // sends 2, hits completionSize - bug not triggered
    
    assertMockEndpointsSatisfied();
}
```