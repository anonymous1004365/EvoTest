---
name: discard-on-completion-timeout-counter
description: When testing an aggregator with discardOnCompletionTimeout(), verify
  that the completedByTimeout counter is correctly incremented and the timeout callback
  is properly invoked. Use this skill when dealing with TimeoutAwareAggregationStrategy
  timeout callbacks combined with discardOnCompletionTimeout.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- EXCEPTION_HANDLING
test_pattern: STATE_TEST
---

# discard-on-completion-timeout-counter

## Instructions

# Discard on Completion Timeout Counter Verification

## Instructions

- WHEN the TG encounters an AggregationStrategy implementing `TimeoutAwareAggregationStrategy` (with a `timeout()` method) combined with `.discardOnCompletionTimeout()` on the aggregator route
  - THEN the TG should write a test that:
    1. Sends fewer exchanges than `completionSize` to trigger the timeout
    2. Verifies that the `timeout()` method on the `TimeoutAwareAggregationStrategy` is invoked exactly once (using a counter like `AtomicInteger` to track invocations)
    3. Verifies that `completedByTimeout` (obtained via `AggregateProcessorStatistics`) is incremented to 1 after the timeout
    4. Verifies the mock endpoint received 0 messages (since `discardOnCompletionTimeout()` discards the partial exchange on timeout)
    5. Then sends enough exchanges to complete normally (hitting `completionSize`) and verifies the timeout method is NOT invoked again (counter stays at 1)

- WHEN the TG tests `discardOnCompletionTimeout()` combined with `TimeoutAwareAggregationStrategy.timeout()` 
  - THEN the TG must verify that the `timeout()` callback receives:
    - The old exchange (not null) with the aggregated body
    - `index == -1`
    - `total == -1`
    - `timeout` equal to the configured `completionTimeout` value
  - Common pitfall: Asserting values inside the `timeout()` method itself. The `timeout()` method contract does NOT allow throwing exceptions (including assertion errors), so all assertions on the received values must be done in the main test thread after capturing them in volatile fields.

- WHEN the TG writes assertions for aggregation timeout behavior
  - THEN the TG should use `mock.assertIsSatisfied(timeout)` with a timeout slightly longer than `completionTimeout` to allow the timeout to fire
  - Common pitfall: Using `mock.assertIsSatisfied()` without a timeout argument could cause the test to hang indefinitely if no messages are expected

- Example (correct approach):
```java
public class DiscardOnTimeoutTest extends ContextTestSupport {
    private final AtomicInteger timeoutInvoked = new AtomicInteger();
    private volatile Exchange capturedExchange;
    private volatile long capturedTimeout;

    public void testDiscardOnTimeoutCount() throws Exception {
        MockEndpoint mock = getMockEndpoint("mock:aggregated");
        mock.expectedMessageCount(0);
        
        // Send only 2 of 3 required - triggers timeout
        template.sendBodyAndHeader("direct:start", "A", "id", 123);
        template.sendBodyAndHeader("direct:start", "B", "id", 123);
        
        mock.assertIsSatisfied(300); // wait for timeout
        
        assertEquals(1, timeoutInvoked.get()); // timeout invoked once
        assertNotNull(capturedExchange);
        assertEquals("AB", capturedExchange.getIn().getBody());
        assertEquals(100L, capturedTimeout);
        
        // Now complete normally
        mock.reset();
        mock.expectedBodiesReceived("ABC");
        template.sendBodyAndHeader("direct:start", "A", "id", 123);
        template.sendBodyAndHeader("direct:start", "B", "id", 123);
        template.sendBodyAndHeader("direct:start", "C", "id", 123);
        mock.assertIsSatisfied(150);
        
        assertEquals(1, timeoutInvoked.get()); // still 1, no new timeout
    }

    @Override
    protected RouteBuilder createRouteBuilder() {
        return new RouteBuilder() {
            public void configure() {
                from("direct:start")
                    .aggregate(header("id"), new MyTimeoutStrategy())
                    .discardOnCompletionTimeout()
                    .completionSize(3)
                    .completionTimeout(100)
                    .completionTimeoutCheckerInterval(10)
                    .to("mock:aggregated");
            }
        };
    }

    private class MyTimeoutStrategy implements TimeoutAwareAggregationStrategy {
        public void timeout(Exchange old, int index, int total, long timeout) {
            timeoutInvoked.incrementAndGet();
            capturedExchange = old;
            capturedTimeout = timeout;
        }
        public Exchange aggregate(Exchange old, Exchange newEx) {
            if (old == null) return newEx;
            old.getIn().setBody(old.getIn().getBody(String.class) 
                + newEx.getIn().getBody(String.class));
            return old;
        }
    }
}
```

- Example (incorrect - asserts inside timeout()):
```java
// WRONG: assertions inside timeout() will be silently swallowed
public void timeout(Exchange old, int index, int total, long timeout) {
    assertEquals(1, something); // This exception is caught and ignored!
}
```