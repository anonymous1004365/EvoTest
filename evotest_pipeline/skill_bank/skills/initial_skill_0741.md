---
name: stream-cache-reset-on-exchange-copy
description: WHEN an exchange is copied for multi-step routing (e.g. RoutingSlip,
  Pipeline, RecipientList), stream caches on the body must be reset after the copy
  so each downstream consumer re-reads from the beginning. This skill teaches how
  to test for stream cache exhaustion when copying exchanges.
code_tags:
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# stream-cache-reset-on-exchange-copy

## Instructions

# Stream Cache Reset on Exchange Copy

## Instructions

- WHEN the TG encounters a method that copies an Exchange (e.g., calling `new DefaultExchange(current)`, `ExchangeHelper.createCorrelatedCopy()`, or `copyOutToIn(copy, current)`) within a processor that routes the exchange through multiple endpoints (like `RoutingSlip`, `Pipeline`, `RecipientList`, or custom aggregators)
- THEN the TG should verify that after each copy, the stream cache on the copy's body is properly reset. Specifically:
  - Look for calls like `MessageHelper.resetStreamCache(copy.getIn())` or `((StreamCache) body).reset()` after the copy operation
  - If reset is missing, write a test that sends a `ByteArrayInputStream` body (or any `StreamCache`-compatible stream body) through a route that processes the exchange at multiple endpoints (e.g., a routing slip with 3 endpoints like `"mock:foo,mock:bar,mock:baz"`)
  - Enable stream caching on the context: `context.setStreamCaching(true)`
  - Assert that each downstream endpoint receives the full, unaltered body (not an empty body)

- WHEN writing such a test, use Camel's `MockEndpoint` assertions like `getMockEndpoint("mock:endpoint").expectedBodiesReceived("<expectedBody/>")` on all endpoints in the route
- THEN verify the test fails on the buggy version (without the `resetStreamCache` call) with the second or subsequent endpoint(s) receiving an empty body — e.g., `"mock://bar Body of message: 0. Expected: <<<hello/>> but was: <>"`

- Common pitfalls to avoid:
  - Testing with only a single endpoint — this masks the bug because the stream cache is consumed only once and never needs resetting
  - Using `String` body types — these are not affected by stream cache exhaustion; use `ByteArrayInputStream` or another `StreamCache`-compatible type
  - Relying on `Thread.sleep()` or timing — the bug is deterministic, not a race condition
  - Forgetting to enable stream caching on the context via `context.setStreamCaching(true)`

### Correct example

```java
public void testByteArrayInputStream() throws Exception {
    getMockEndpoint("mock:foo").expectedBodiesReceived("<hello/>");
    getMockEndpoint("mock:bar").expectedBodiesReceived("<hello/>");
    getMockEndpoint("mock:baz").expectedBodiesReceived("<hello/>");

    template.sendBodyAndHeader("direct:a", new ByteArrayInputStream("<hello/>".getBytes()), 
                               "mySlip", "mock:foo,mock:bar,mock:baz");

    assertMockEndpointsSatisfied();
}
```

### Incorrect example (will not catch the bug)

```java
// WRONG: Single endpoint — stream is consumed once, never needs reset
public void testByteArrayInputStream() throws Exception {
    getMockEndpoint("mock:foo").expectedBodiesReceived("<hello/>");

    template.sendBodyAndHeader("direct:a", new ByteArrayInputStream("<hello/>".getBytes()), 
                               "mySlip", "mock:foo");

    assertMockEndpointsSatisfied();
}
```

```java
// WRONG: String body — String is not a stream, so no stream cache issue occurs
public void testStringBody() throws Exception {
    getMockEndpoint("mock:foo").expectedBodiesReceived("<hello/>");
    getMockEndpoint("mock:bar").expectedBodiesReceived("<hello/>");

    template.sendBodyAndHeader("direct:a", "<hello/>", "mySlip", "mock:foo,mock:bar");

    assertMockEndpointsSatisfied();
}
```