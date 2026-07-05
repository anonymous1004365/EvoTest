---
name: aggregate-completion-size-expression-override
description: Teaches how to test that when an aggregate route defines both a static
  completionSize and a completionSize expression (header-based), the expression value
  overrides the static value. Use this skill when testing Camel aggregator routes
  with multiple completion size configurations.
code_tags:
- THREADING_SYNCHRONIZATION
- STATE_MUTATION
- AGGREGATION_EXCEPTION_PROPAGATION
test_pattern: STATE_TEST
---

# aggregate-completion-size-expression-override

## Instructions

# Aggregate Completion Size Expression Override

## Instructions

- WHEN the TG encounters a Camel `aggregate()` route where both `.completionSize(int)` (static integer) and `.completionSize(header("someHeader"))` (dynamic expression) are configured:
  - THEN the TG MUST verify that the expression-based completion size overrides the static integer completion size.
  - Specifically, if `.completionSize(2)` is set before `.completionSize(header("mySize"))` with `mySize=3`, the aggregator MUST wait for 3 messages, not 2, before completing.

- WHEN the TG writes a test for this override behavior:
  - THEN the TG MUST include a route like `.completionSize(2).completionSize(header("mySize"))` where the header value is larger than the static value (e.g., 3 > 2).
  - THEN the TG MUST send exactly 3 messages with the same correlation key (e.g., `header("id")` set to a common value like 123) and the header `"mySize"` set to 3.
  - THEN the TG MUST assert that `mock:aggregated` receives a body containing all three messages combined (e.g., `"A+B+C"`), NOT just the first two.
  - THEN the TG MUST also assert the property `Exchange.AGGREGATED_COMPLETED_BY` equals `"size"` to verify the completion was triggered by the size condition.

- Common pitfalls to avoid:
  - Do NOT test only the static `.completionSize(int)` in isolation — the bug is specifically about the expression overriding the static value, so both must be present.
  - Do NOT use a header value that is smaller than or equal to the static value (e.g., `.completionSize(2).completionSize(header("mySize"))` with `mySize=2`), because that would not differentiate between the two settings and could pass on the buggy version.
  - Do NOT test with only 2 messages when the expression expects 3 — the buggy version incorrectly completes after 2 messages (the static value) instead of waiting for 3 (the expression value).
  - Do NOT forget to set the correlation key header and the completion size header on each message — the aggregator groups by correlation key and uses the expression to evaluate completion size.
  - Do NOT use a completion timeout (`completionTimeout`) in the same route, as it could mask the size-based completion bug by completing the group early due to timeout.

### Correct Example

```java
public void testCompletionSizeExpressionOverridesStaticSize() throws Exception {
    getMockEndpoint("mock:aggregated").expectedBodiesReceived("A+B+C");
    getMockEndpoint("mock:aggregated").expectedPropertyReceived(Exchange.AGGREGATED_COMPLETED_BY, "size");

    Map<String, Object> headers = new HashMap<>();
    headers.put("id", 123);
    headers.put("mySize", 3);

    template.sendBodyAndHeaders("direct:start", "A", headers);
    template.sendBodyAndHeaders("direct:start", "B", headers);
    template.sendBodyAndHeaders("direct:start", "C", headers);

    assertMockEndpointsSatisfied();
}

@Override
protected RouteBuilder createRouteBuilder() throws Exception {
    return new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start")
                .aggregate(header("id"), new BodyInAggregatingStrategy())
                    .completionSize(2).completionSize(header("mySize"))
                    .to("mock:aggregated");
        }
    };
}
```

### Incorrect Example (would pass on buggy version, missing the bug)

```java
// WRONG: Tests only the static completion size, does not test override behavior
public void testWrongApproach() throws Exception {
    getMockEndpoint("mock:aggregated").expectedBodiesReceived("A+B");

    Map<String, Object> headers = new HashMap<>();
    headers.put("id", 123);

    template.sendBodyAndHeaders("direct:start", "A", headers);
    template.sendBodyAndHeaders("direct:start", "B", headers);

    assertMockEndpointsSatisfied();
}
```

### Common Pitfalls (Code to Avoid)

```java
// WRONG: Only 2 messages — would pass on buggy version but fails to detect the bug
getMockEndpoint("mock:aggregated").expectedBodiesReceived("A+B");
template.sendBodyAndHeaders("direct:start", "A", headers);
template.sendBodyAndHeaders("direct:start", "B", headers);

// WRONG: Header value equals static value — cannot distinguish override behavior
headers.put("mySize", 2); // same as static .completionSize(2)

// WRONG: Using completionTimeout which could complete the group before size is reached
.completionSize(2).completionSize(header("mySize")).completionTimeout(100)
```