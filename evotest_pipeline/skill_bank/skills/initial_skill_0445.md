---
name: exception-propagation-in-streaming-splitter
description: WHEN testing streaming splitter with error handling, THEN verify that
  exceptions from sub-exchanges during streaming are properly propagated to the result
  exchange. This skill helps detect bugs where exceptions silently fail to reach the
  caller when using .streaming() on a splitter with the default aggregation strategy.
code_tags:
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# exception-propagation-in-streaming-splitter

## Instructions

# Exception Propagation in Streaming Splitter

## Instructions

- WHEN the TG encounters a Splitter EIP with `.streaming()` mode AND no custom aggregation strategy (i.e., relying on the default `UseOriginalAggregationStrategy`)
- THEN the TG should write a test that sends a message body that causes one of the split parts to throw an exception (e.g., `IllegalArgumentException`) while other parts succeed, and verify that the exception is propagated to the caller as a `CamelExecutionException`
- Specifically, configure a route like: `from("direct:start").split(body().tokenize(",")).streaming().process(...).end().to("mock:result")` where the processor throws an exception for one specific body value (e.g., "Kaboom")
- Verify that `mock:result` receives **zero** messages (expectedMessageCount(0)) — because the exception should prevent the final aggregation
- Verify that the exception is caught as a `CamelExecutionException` and the root cause is the expected exception type with the expected message
- ALSO verify that the successfully processed split messages were actually sent to intermediate mocks (e.g., `mock:a` receives all parts including the failing one; `mock:b` receives only the successful ones)
- **Common pitfalls to avoid**:
  - Testing only the non-streaming case — the bug manifests specifically with `.streaming()` mode
  - Forgetting to set `expectedMessageCount(0)` on the final result endpoint — the bug causes the final aggregated output to appear when it shouldn't
  - Not checking intermediate mock endpoints to confirm partial processing occurred before the exception
  - Assuming that `stopOnException` must be set — the bug occurs with the default (stopOnException=false) because streaming mode fails to propagate the exception through the aggregation strategy

### Correct Example (the bug-catching test)

```java
public void testSplitterStreamingWithError() throws Exception {
    getMockEndpoint("mock:a").expectedBodiesReceived("A", "B", "Kaboom", "D", "E");
    getMockEndpoint("mock:b").expectedBodiesReceived("A", "B", "D", "E");
    getMockEndpoint("mock:result").expectedMessageCount(0);

    try {
        template.sendBody("direct:start", "A,B,Kaboom,D,E");
        fail("Should have thrown an exception");
    } catch (CamelExecutionException e) {
        assertIsInstanceOf(IllegalArgumentException.class, e.getCause());
        assertEquals("Cannot do this", e.getCause().getMessage());
    }

    assertMockEndpointsSatisfied();
}

@Override
protected RouteBuilder createRouteBuilder() throws Exception {
    return new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start")
                .split(body().tokenize(",")).streaming()
                    .to("mock:a")
                    .process(new Processor() {
                        public void process(Exchange exchange) throws Exception {
                            String body = exchange.getIn().getBody(String.class);
                            if ("Kaboom".equals(body)) {
                                throw new IllegalArgumentException("Cannot do this");
                            }
                        }
                    })
                    .to("mock:b")
                .end()
                .to("mock:result");
        }
    };
}
```

### Incorrect Example (would miss the bug)

```java
// BUGGY: Non-streaming splitter does not trigger the bug
public void testSplitterNonStreamingWithError() throws Exception {
    getMockEndpoint("mock:result").expectedBodiesReceived("A,B,C,D,E");
    // ... sends body without Kaboom, never tests exception propagation
    template.sendBody("direct:start", "A,B,C,D,E");
    assertMockEndpointsSatisfied();
    // This test passes on both buggy and fixed versions — useless!
}

// BUGGY: No exception capturing — silently passing
public void testSplitterStreamingWithError() throws Exception {
    getMockEndpoint("mock:a").expectedBodiesReceived("A", "B", "Kaboom", "D", "E");
    getMockEndpoint("mock:result").expectedBodiesReceived("A,B,C,D,E"); // BUG: should be 0!
    
    template.sendBody("direct:start", "A,B,Kaboom,D,E");
    // Missing try-catch — the exception is swallowed, test passes on buggy version!
    assertMockEndpointsSatisfied();
}
```