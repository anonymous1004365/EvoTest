---
name: aggregated-list-body-preservation
description: When using AbstractListAggregationStrategy with .split() and .end(),
  the TG should test that aggregated List data is correctly stored on the completed
  message body. The bug causes the aggregated list to be missing or of wrong type
  when using custom aggregation strategies with split, because onCompletion's setBody
  is not triggered.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- BOUNDARY_CHECK
- AGGREGATION_STRATEGY_LIST_MUTATION
test_pattern: STATE_TEST
---

# aggregated-list-body-preservation

## Instructions

# List Body Preservation in Aggregation-Completion with Split

## Instructions

- WHEN the TG encounters a route using `.split(body(), new CustomAggregationStrategy())` where `CustomAggregationStrategy` extends `AbstractListAggregationStrategy<V>` (with `isStoreAsBodyOnCompletion()` defaulting to `true`), THEN the TG should write a test that:
  1. Sends a `List<String>` of multiple values (e.g., `["100", "150", "130"]`) to the route's starting endpoint
  2. Verifies that the final `mock:result` endpoint receives exactly 1 message
  3. Verifies that the body of that message is an instance of `java.util.List` via `result.message(0).body().isInstanceOf(List.class)`
  4. Retrieves the aggregated list from `result.getExchanges().get(0).getIn().getBody(List.class)` and asserts its elements by index, with correct generic type (e.g., `Integer`)
- WHEN the aggregation strategy extends `AbstractListAggregationStrategy<Integer>` with `getValue(Exchange)` converting `String` body to `Integer`, THEN the TG should verify the aggregated list contains the expected converted values (e.g., `assertEquals(Integer.valueOf("100"), numbers.get(0))`), NOT raw `String` values.
- WHEN the route uses `.split(body(), strategy).end()`, the TG must ensure the `mock:result` endpoint receives the final aggregated exchange AFTER `end()`, NOT an intermediate split exchange.
- Common pitfalls to avoid:
  - NOT verifying the body is a `List` instance at the mock level — the buggy behavior leaves the body as the raw last split element instead of the aggregated list
  - Testing only the `List` size but not element types/index values
  - Using the aggregation strategy without `.split()` — the bug only manifests when aggregation is used inside a splitter context where `onCompletion` may not be called
  - Assuming `getBody(List.class)` returns the correct generic type without checking actual element types

### Example (Correct test approach):

```java
public void testCustomAggregationStrategy() throws Exception {
    getMockEndpoint("mock:line").expectedBodiesReceived(100, 150, 130);
    MockEndpoint result = getMockEndpoint("mock:result");
    result.expectedMessageCount(1);
    result.message(0).body().isInstanceOf(List.class);

    List<String> body = new ArrayList<>();
    body.add("100");
    body.add("150");
    body.add("130");
    template.sendBody("direct:start", body);
    assertMockEndpointsSatisfied();

    List<Integer> numbers = result.getExchanges().get(0).getIn().getBody(List.class);
    assertNotNull(numbers);
    assertEquals(Integer.valueOf("100"), numbers.get(0));
    assertEquals(Integer.valueOf("150"), numbers.get(1));
    assertEquals(Integer.valueOf("130"), numbers.get(2));
}
```

### Example (Incorrect — missing body type check):

```java
public void testCustomAggregationStrategy() throws Exception {
    MockEndpoint result = getMockEndpoint("mock:result");
    result.expectedMessageCount(1);
    // BUG: missing result.message(0).body().isInstanceOf(List.class)
    // The test will pass even if the body is NOT a List

    template.sendBody("direct:start", List.of("100", "150", "130"));
    assertMockEndpointsSatisfied();
    // This will fail at runtime with ClassCastException on the buggy version
    // because the body is still a String, not a List
    List<Integer> numbers = result.getExchanges().get(0).getIn().getBody(List.class);
    assertNotNull(numbers);
}
```