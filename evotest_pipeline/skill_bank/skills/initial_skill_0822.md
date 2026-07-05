---
name: custom-aggregation-strategy-oncompletion-batch
description: When a custom AbstractListAggregationStrategy overrides onCompletion
  to propagate aggregated results, the TG should test that onCompletion is correctly
  invoked with the final aggregated exchange during batch consumption from a batch
  consumer (e.g. file consumer).
code_tags:
- AGGREGATION_EXCEPTION_PROPAGATION
test_pattern: INTERACTION_TEST
---

# custom-aggregation-strategy-oncompletion-batch

## Instructions

# Custom AggregationStrategy onCompletion with Batch Consumer

## Instructions

- WHEN the TG encounters an `AbstractListAggregationStrategy` subclass that overrides `onCompletion(Exchange exchange)` to propagate aggregated results (e.g., setting a property or body on the original exchange) and the route uses a batch consumer (e.g., `from("file:...")`):
  - THEN the TG should write a test that verifies the aggregated result actually reaches the final endpoint after the batch completes.
  - Use a mock endpoint (e.g., `mock:result`) to assert that the correct number of messages (e.g., 1 aggregated result) is received.
  - Set up the route to consume from a batch consumer and use `completionSize(2)` (or similar) to trigger completion after a known number of messages.
  - Send the expected number of messages into the route, then verify the mock endpoint receives exactly 1 message containing the aggregated result.
  - Also verify that the `onCompletion` method was called by inspecting the exchange properties set during `onCompletion`.

- WHEN validating `onCompletion` behavior in batch mode:
  - THEN the TG should verify that the `Exchange.AGGREGATED_COMPLETED_EXCHANGES` property is properly handled during completion.
  - Use `exchange.removeProperty(Exchange.AGGREGATED_COMPLETED_EXCHANGES)` in the `onCompletion` override — this is the key operation that propagates the aggregated list to the final exchange.
  - The test should fail if the final mock endpoint receives 0 messages (batched messages were not aggregated and completed).

- Common pitfalls to avoid:
  - Testing `onCompletion` without a batch consumer — the bug only manifests when the `Aggregator` routes through the batch consumer completion path (where `onCompletion` is called on the aggregated exchange).
  - Testing only the aggregation logic (e.g., `aggregate()` method) without testing the completion lifecycle — `onCompletion` is only invoked when a completion strategy triggers the completion of the batch.
  - Using `direct:` endpoints instead of batch consumer endpoints — the bug requires a consumer that sends the `Exchange.BATCH_COMPLETE` header.
  - Forgetting to set `completionSize` or another completion predicate to trigger batch completion.

### Example: Correct test structure

```java
// Setup route with batch consumer
RouteBuilder builder = new RouteBuilder() {
    @Override
    public void configure() throws Exception {
        from("direct:start")
            .aggregate(new MyCustomListStrategy())
                .header("aggregateId")
                .completionSize(2)
                .to("mock:result");
    }
};

// Send messages and verify
template.sendBodyAndHeader("direct:start", "A", "aggregateId", "1");
template.sendBodyAndHeader("direct:start", "B", "aggregateId", "1");
mockResult.expectedMessageCount(1);
mockResult.assertIsSatisfied();
Exchange result = mockResult.getExchanges().get(0);
// Verify aggregated property was set by onCompletion
List<?> aggregated = result.getProperty("myAggregatedList", List.class);
assertNotNull(aggregated);
assertEquals(2, aggregated.size());
```

### Example: Incorrect test (misses the bug)

```java
// WRONG: Only testing aggregate() directly, skipping batch completion lifecycle
MyCustomListStrategy strategy = new MyCustomListStrategy();
Exchange oldEx = ...;
Exchange newEx = ...;
Exchange result = strategy.aggregate(oldEx, newEx);
// This does NOT test onCompletion, so the bug where onCompletion
// doesn't propagate results will NOT be caught
```