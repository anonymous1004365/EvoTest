---
name: empty-split-aggregation-null-exchange
description: When a Splitter iterates over zero elements, a custom AggregationStrategy
  that implements CompletionAwareAggregationStrategy receives a null oldExchange in
  the onCompletion callback. This skill teaches how to test that the aggregation strategy
  handles null exchanges gracefully when the split body is empty.
code_tags:
- STATE_MUTATION
- NULL_CHECK
- SAFE_COPY
test_pattern: EXCEPTION_TEST
---

# empty-split-aggregation-null-exchange

## Instructions

# Empty Split Aggregation Null Exchange Handling

## Instructions

WHEN a route uses a Splitter EIP with a custom AggregationStrategy that implements `CompletionAwareAggregationStrategy`, AND the split body evaluates to an empty collection (zero elements to split):

- THEN the aggregator's `onCompletion(Exchange exchange)` callback receives an `exchange` whose body is `null` (the aggregated exchange body).
- The TG MUST write a test that sets up a route using `.split().body().aggregationStrategy(myStrategy)` where `myStrategy` is an `AggregationStrategy` that also implements `CompletionAwareAggregationStrategy`, sends a message with an empty list/array body to the route, and verifies that no `NullPointerException` or unexpected error occurs in the `onCompletion` callback.
- The test MUST specifically target the empty-split edge case: the split iterates zero times, so `oldExchange` is never set by a previous aggregation; the `onCompletion` callback therefore runs with a null aggregated exchange.
- Verify correctness by asserting that the final exchange body (or a header/property set during aggregation) reflects the expected empty-list result (e.g., `assertNotNull(exchange.getProperty(Exchange.GROUPED_EXCHANGE))` if using `GroupedExchangeAggregationStrategy`, or a custom list body that is empty).
- Common pitfall: Testing only with non-empty split bodies (1+ elements) passes even if the aggregation strategy contains a null-unsafe `onCompletion`. The TG MUST explicitly test the empty-split scenario to catch the bug.
- Another common pitfall: Assuming the `onCompletion` callback is never invoked when the split body is empty — it IS invoked with a null exchange body, and the strategy must handle it.

### Example (Correct — catches the bug)

```java
// Given: MyCustomStrategy extends AbstractListAggregationStrategy and implements CompletionAwareAggregationStrategy
// When: split body is an empty list
// Then: no NullPointerException should be thrown

public class MyCustomStrategyEmptySplitTest extends ContextTestSupport {

    @Override
    protected RouteBuilder createRouteBuilder() {
        return new RouteBuilder() {
            @Override
            public void configure() {
                from("direct:start")
                    .split(body()).aggregationStrategy(new MyCustomStrategy())
                    .to("mock:result");
            }
        };
    }

    @Test
    public void testEmptySplit() {
        MockEndpoint mock = getMockEndpoint("mock:result");
        mock.expectedMessageCount(1);

        // Send an empty list — zero elements to split
        template.sendBody("direct:start", new ArrayList<>());

        assertMockEndpointsSatisfied();
        // The aggregated exchange should have an empty body, not throw NPE
        assertNotNull(exchange.getProperty(Exchange.GROUPED_EXCHANGE));
    }
}
```

### Example (Incorrect — misses the bug)

```java
// WRONG: Only tests with a non-empty split body
@Test
public void testNonEmptySplit() {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(1);
    template.sendBody("direct:start", Arrays.asList("a", "b", "c"));
    assertMockEndpointsSatisfied();
}
// This test would pass even if onCompletion throws NPE for empty split!
```