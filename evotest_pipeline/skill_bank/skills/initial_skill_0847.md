---
name: grouped-exchange-exception-propagation
description: When using GroupedExchangeAggregationStrategy with multicast, test that
  the aggregated result does not carry failure/exceptions from individual endpoints
  — the grouped exchange should remain unfailed even when a sub-route throws an exception.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# grouped-exchange-exception-propagation

## Instructions

# Grouped Exchange Exception Propagation in Multicast

## Instructions

- WHEN the TG encounters code using `GroupedExchangeAggregationStrategy` (or its parent `AbstractListAggregationStrategy`) with a `multicast()` or `split()` DSL that sends to multiple endpoints where at least one endpoint may throw an exception
- THEN the TG should write an integration test that:
  1. Creates a route using `multicast(new GroupedExchangeAggregationStrategy())` sending to multiple endpoints (e.g., `mock:endpointA`, `mock:endpointB`)
  2. Configures one of the endpoint processors (e.g., using `whenAnyExchangeReceived`) to throw an `IllegalArgumentException("Fake exception")` on the **first** endpoint in the multicast list
  3. Sends a message body (e.g., `"dummy"`) to the route starting endpoint
  4. Asserts that the aggregated exchange received at the final `mock:result` endpoint:
     - Is **not** failed (i.e., `exchange.isFailed()` returns `false`)
     - The test expects `assertThat("no exception", received.isFailed(), is(false))` to pass
- The common mistake to avoid: assuming that an exception from one multicast branch will propagate to the aggregated result exchange. The `GroupedExchangeAggregationStrategy` collects the individual exchanges as a list in the message body and should NOT mark the aggregated exchange as failed even when some sub-exchanges failed.

### Correct Test Example
```java
public void testFirstEndpointFails() throws Exception {
    MockEndpoint result = getMockEndpoint("mock:result");
    result.expectedMessageCount(1);

    MockEndpoint endpointA = getMockEndpoint("mock:endpointA");
    endpointA.whenAnyExchangeReceived(new Processor() {
        @Override
        public void process(Exchange exchange) throws Exception {
            throw new IllegalArgumentException("Fake exception");
        }
    });

    template.sendBody("direct:start", "dummy");
    assertMockEndpointsSatisfied();

    Exchange received = result.getReceivedExchanges().get(0);
    assertThat("no exception", received.isFailed(), is(false));
}
```

### Route Setup Example
```java
from("direct:start")
    .multicast(new GroupedExchangeAggregationStrategy())
        .to("mock:endpointA", "mock:endpointB")
    .end()
    .to("mock:result");
```

### Common Pitfall (Incorrect Test)
```java
// WRONG: Expecting an exception to propagate to the aggregated result
public void testEndpointFails_Wrong() throws Exception {
    try {
        template.sendBody("direct:start", "dummy");
        fail("Should have thrown an exception");
    } catch (CamelExecutionException e) {
        // Wrong! The grouped exchange aggregation strategy swallows branch exceptions
    }
}
```