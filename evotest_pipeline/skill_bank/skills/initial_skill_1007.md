---
name: async-loop-copy-preservation
description: ''
code_tags:
- STATE_MUTATION
- ORDER_DEPENDENCY
- CONCURRENCY
test_pattern: INTERACTION_TEST
---

# async-loop-copy-preservation

## Instructions

# Asynchronous Loop with Copy Mode — Exchange Body Preservation

## Instructions

- WHEN the TG encounters a `LoopProcessor` configured with `copy=true` (e.g., via `.loop(...).copy().end()` in a Camel RouteBuilder) AND the route processes the exchange through an asynchronous processor (such as `MyAsyncComponent` or any component that completes the exchange on a different thread),
- THEN the TG MUST write a test that verifies the **original exchange's body is preserved** after the loop completes. Specifically:
  - Use an async component (e.g., `"async:bye:camel"` from `MyAsyncComponent`) inside the loop that transforms the body.
  - Set up mock endpoints at these positions:
    - `mock:before` — before the loop (should receive the original body)
    - `mock:loopIterationStart` — inside the loop, before processing (should receive the original body on each iteration)
    - `mock:loopIterationEnd` — inside the loop, after processing (should receive the transformed body on each iteration)
    - `mock:result` — after the loop ends (should receive the **original** body, unchanged)
  - Use `template.requestBodyAndHeader()` to trigger the route with a body and a header specifying the loop count, and assert the reply equals the original body.
  - Verify the mock endpoints' expectations with `assertMockEndpointsSatisfied()`.

- Common pitfalls to avoid:
  - Testing only with synchronous processors (the bug manifests only with async processing, as the async callback path in `LoopProcessor.process(Exchange, AsyncCallback)` mutates the exchange object in-place and then applies `ExchangeHelper.copyResults(exchange, target)` where `exchange` is the shared mutable exchange rather than a fresh copy for each iteration).
  - Forgetting to assert that `mock:loopIterationStart` receives the **original** body (e.g., `"Hello Camel"`) on each iteration — this verifies each loop iteration starts from a clean copy of the original and is not polluted by previous iterations' mutations.
  - Asserting only the final result body matches but not checking intermediate mock endpoints — the bug causes `mock:loopIterationStart` to receive `"Bye Camel"` (the mutated body) instead of `"Hello Camel"` when `copy=true` but async processing mutates the shared exchange.

### Correct test approach (matches `AsyncLoopCopyTest.testAsyncLoopCopy`):

```java
public void testAsyncLoopCopy() throws Exception {
    // mock:before receives original body exactly once
    getMockEndpoint("mock:before").expectedBodiesReceived("Hello Camel");
    
    // Each iteration should start from a fresh copy of the original
    getMockEndpoint("mock:loopIterationStart").expectedBodiesReceived("Hello Camel", "Hello Camel");
    
    // After async processing, body is transformed
    getMockEndpoint("mock:loopIterationEnd").expectedBodiesReceived("Bye Camel", "Bye Camel");
    
    // After loop ends, the final exchange should have the original body
    getMockEndpoint("mock:result").expectedBodiesReceived("Hello Camel");

    String reply = template.requestBodyAndHeader("direct:start", "Hello Camel", "NumberIterations", 2, String.class);
    assertEquals("Hello Camel", reply);
    
    assertMockEndpointsSatisfied();
}
```

With route:

```java
from("direct:start")
    .to("mock:before")
    .loop(header("NumberIterations")).copy()
        .to("mock:loopIterationStart")
        .to("async:bye:camel")  // transforms body from "Hello Camel" to "Bye Camel"
        .to("mock:loopIterationEnd")
    .end()
    .to("mock:result");
```

### Incorrect approach (would miss the bug):

```java
// ❌ Testing only with synchronous processor inside loop — won't exercise the buggy async path
from("direct:start")
    .loop(header("NumberIterations")).copy()
        .bean(someBean)  // synchronous transformation
    .end()
    .to("mock:result");

// ❌ Not checking mock:loopIterationStart — the bug causes iteration start to show mutated body
// ❌ Not verifying the returned reply body equals the original input
// ❌ Using only requestBody() instead of requestBodyAndHeader() to pass loop count
```