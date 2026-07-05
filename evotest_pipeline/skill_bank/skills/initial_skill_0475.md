---
name: bean-before-aggregate-state-recovery
description: WHEN a test uses a bean method (via .bean()) before an aggregator in
  a Camel route, and the bean throws an exception (e.g., NullPointerException), THEN
  the test must verify that the aggregation repository state is properly recovered/cleaned
  up and that subsequent exchanges can be aggregated without stale state from the
  failed exchange.
code_tags:
- SINGLETON_REGISTRY
- STATE_MUTATION
- AGGREGATION_EXCEPTION_PROPAGATION
test_pattern: STATE_TEST
---

# bean-before-aggregate-state-recovery

## Instructions

# Bean-Before-Aggregate State Recovery

## Instructions

- WHEN a Camel route uses `.bean(SomeBean.class)` or `.bean(ref, "methodName")` followed by `.aggregate(header, strategy)` and the bean method throws an exception (e.g., `NullPointerException` on a null body header like `"cheese"`)
- THEN the TG should write a test that:
  1. Defines a route: `.bean(BodyInAggregatingStrategy.class).aggregate(header("cheese"), new BodyInAggregatingStrategy()).completionSize(2).aggregationRepository(new MemoryAggregationRepository()).to("mock:result")`
  2. Sends a first message **with a null value** for the aggregation header (e.g., `template.sendBodyAndHeader("direct:start", "A", "cheese", null)`) — the bean will throw an exception when trying to call `exchange.getIn().getBody(String.class)` on a null header
  3. Verifies that the first exchange fails (causes an exception on the error handler / mock endpoint receives no messages from that exchange)
  4. Then sends a second message **with a valid header value** (e.g., `template.sendBodyAndHeader("direct:start", "B", "cheese", "CHEESE")`)
  5. Asserts that the second exchange is **successfully aggregated** and delivered to `mock:result` — this confirms the aggregation repository was cleaned up and is not stuck with stale state from the failed first exchange
  6. Also verify that the total number of messages received at `mock:result` is exactly `1` (only the second, successful exchange arrived)
- Common pitfalls to avoid:
  ❌ **Sending both messages without the null-header case** — this would not expose the repository state leak
  ❌ **Only testing with `MemoryAggregationRepository` but forgetting to ensure it's a fresh instance for each test** — stale state from previous tests could mask the bug
  ❌ **Forgetting to mark the route as not handling exceptions** (i.e., no `.handled(true)`) — the exception from the bean must propagate and trigger the repository cleanup path in `AggregateProcessor`
  ❌ **Using an aggregation strategy that produces different output for null vs. non-null** — the strategy should simply concatenate bodies for clarity
  ❌ **Not verifying the mock endpoint received exactly 1 message** — verifying only that "no exceptions occur" is insufficient; you must count delivered messages

**Correct example:**
```java
public void testBeanBeforeAggregation() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(1);

    // First: send a message with null header — bean throws, exchange fails
    template.sendBodyAndHeader("direct:start", "A", "cheese", null);
    // Second: send a valid message
    template.sendBodyAndHeader("direct:start", "B", "cheese", "CHEESE");

    assertMockEndpointsSatisfied();
    assertEquals("B", mock.getExchanges().get(0).getIn().getBody(String.class));
}
```

**Incorrect example (would NOT catch the bug):**
```java
public void testBeanBeforeAggregation() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(2);  // WRONG: first exchange failed, never arrives

    template.sendBodyAndHeader("direct:start", "A", "cheese", "CHEESE1");
    template.sendBodyAndHeader("direct:start", "B", "cheese", "CHEESE2");

    assertMockEndpointsSatisfied();
}
```