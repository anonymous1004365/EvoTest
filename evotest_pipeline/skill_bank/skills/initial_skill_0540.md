---
name: advice-with-endpoint-interception-parameter-sensitivity
description: When using adviceWith or interceptSendToEndpoint in Camel, the mock endpoint
  URI may differ from the original producer URI in query parameters or ordering. This
  skill teaches how to test that the adviceWith correctly intercepts the right producer
  despite URI parameter differences.
code_tags:
- ADVICE_WITH_ROUTE_INTERCEPTION
- URI_MATCHING_PARAMETER_SENSITIVITY
test_pattern: INTERACTION_TEST
---

# advice-with-endpoint-interception-parameter-sensitivity

## Instructions

# AdviceWith Endpoint Interception: URI Parameter Sensitivity in Intercept Matching

## Instructions

WHEN the TG encounters a test using `adviceWith()` or `interceptSendToEndpoint()` where the original route's `to()` endpoint has query parameters and the mock replacement endpoint also has query parameters (possibly overlapping, missing, or in a different order),

THEN the TG should ensure that the mock endpoint URI contains all necessary query parameters that the original producer URI had for the interception to match correctly. Specifically:

- The `interceptSendToEndpoint()` or `adviceWith` mock endpoint URI must match the original producer `to()` URI pattern. If the original `to("direct:out?param1=value1")` is intercepted by replacing with `mock:out`, the interception may fail because the parameter `param1=value1` is present in the producer URI but absent in the mock URI, causing a mismatch.
- The TG should verify that when a producer URI with query parameters is intercepted via `mock:endpoint`, the mock endpoint URI **must include the same query parameters** as the original producer URI for the Camel interception mechanism to match correctly.
- The TG should create a route with a producer endpoint that includes query parameters (e.g., `direct:out?param1=value1`), then use `adviceWith` to replace that endpoint with a mock endpoint (e.g., `mock:out`). The test should verify that **sending a message to the route's input endpoint triggers the mock endpoint and the exchange arrives at the test**.
- Common pitfalls:
  - Using `mock:endpoint` when the original has `direct:endpoint?param=value`. The parameters are part of the endpoint identity in Camel URI matching.
  - Assuming parameters are optional or ignored during interception — they are NOT.
  - Forgetting that `interceptSendToEndpoint` uses pattern matching and the mock replacement must preserve parameter identity for the route to function correctly.

**Correct approach (test that reveals the bug):**
```java
// The producer uses direct:out with a query parameter
from("direct:in").to("direct:out?param1=value1");

// The adviceWith must use the same parameter in the mock URI
context.getRouteDefinitions().get(0).adviceWith(context, new AdviceWithRouteBuilder() {
    @Override
    public void configure() throws Exception {
        weaveByToUri("direct:out\\?param1=value1").replace().to("mock:out?param1=value1");
    }
});
```

**Incorrect approach (hides the bug / fails to detect it):**
```java
// Incorrect: using mock endpoint without the parameter that exists in the original
context.getRouteDefinitions().get(0).adviceWith(context, new AdviceWithRouteBuilder() {
    @Override
    public void configure() throws Exception {
        weaveByToUri("direct:out\\?param1=value1").replace().to("mock:out"); // MISSING param1=value1
    }
});
// This may cause the interception to not match, and the exchange goes to the original endpoint
```

WHEN writing such a test, the TG should verify:
- That the mock endpoint receives the expected exchange.
- That if the mock URI omits parameters present in the intercepted endpoint's URI, the test will fail on the buggy version (no message arrives at mock).
- The test should use `context.setUseAdviceWith(true)` and manually start the context after applying adviceWith.