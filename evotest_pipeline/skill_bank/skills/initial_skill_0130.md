---
name: routing-slip-invalid-endpoint-error-handler-bypass
description: ''
code_tags:
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# routing-slip-invalid-endpoint-error-handler-bypass

## Instructions

# Routing Slip Invalid Endpoint Error Handler Bypass

## Instructions

**WHEN** the TG encounters a `RoutingSlip` (or `@RoutingSlip` annotation) that evaluates an expression to produce endpoint URIs at runtime, and the route uses an error handler (e.g., `DeadLetterChannel` or `defaultErrorHandler`) or `noErrorHandler()`:

- **THEN** the TG MUST write a test that sends a message to a route containing `routingSlip()` where one of the resolved endpoints is **invalid** (a URI that cannot produce a valid endpoint, such as `"fail:endpoint"` or `"NonExistingEndpoint:foo"`).

- **THEN** the TG MUST verify that when the routing slip expression resolves an invalid endpoint, the **error handler is invoked** (i.e., the exchange is sent to the `deadLetterUri` or `onException` handler) **unless** the route explicitly calls `.noErrorHandler()`.

- **THEN** the TG MUST NOT assume the routing slip silently skips invalid endpoints when `ignoreInvalidEndpoints` is `false` (the default). The default behavior should trigger the error handler, not swallow the exception.

- **THEN** the TG MUST use `mock:error` or `mock:dead` as the dead letter channel URI and assert that the mock endpoint receives the original message (i.e., `mock:error` should have `expectedMessageCount(1)`).

- **THEN** the TG MUST also verify that no message reaches the *next* valid endpoint after the invalid one (e.g., `mock:end` should have `expectedMessageCount(0)`), because the error handler should intervene.

### Common Pitfalls

- ❌ **Testing only the `ignoreInvalidEndpoints=true` case** — this bypasses the error handler intentionally. Without this skill, a TG might write a test that only passes because invalid endpoints are ignored.

- ❌ **Assuming `DeadLetterChannel` is the default** — in some Camel versions, the default error handler may re-deliver or just log. Use an explicit `.errorHandler(deadLetterChannel("mock:error"))` to be unambiguous.

- ❌ **Forgetting that `routingSlip()` with no error handler set** still inherits the default error handler. The test should *set* an error handler to verify it fires, rather than relying on defaults.

- ❌ **Testing with `noErrorHandler()` and expecting error handler invocation** — the TG must distinguish between a route that disables error handling and one that keeps it. When `noErrorHandler()` is called, no error handler fires, and the exchange should fail with an exception.

### Correct Example

```java
public class RoutingSlipInvalidEndpointNoSuchEndpointExceptionTest extends ContextTestSupport {

    @Test
    public void testRoutingSlipNoErrorHandlerChild() throws Exception {
        context.getRouteDefinitions().clear();
        context.addRoutes(new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                errorHandler(deadLetterChannel("mock:error").maximumRedeliveries(0));

                from("direct:start")
                    .routingSlip(header("slip"));
                
                from("direct:child")
                    .to("mock:end");
            }
        });

        // The slip resolves to an invalid endpoint first, then a valid one.
        // The invalid endpoint should trigger the error handler.
        getMockEndpoint("mock:error").expectedMessageCount(1);
        getMockEndpoint("mock:end").expectedMessageCount(0);

        template.sendBodyAndHeader("direct:start", "Hello World", "slip",
            "NonExistingEndpoint:foo,direct:child");

        assertMockEndpointsSatisfied();
    }
}
```

### Incorrect Example (without this skill)

```java
// WRONG: tests only the ignoreInvalidEndpoints=true case, 
// or tests with no error handler set and assumes behavior.
public class IncompleteRoutingSlipTest extends ContextTestSupport {
    @Test
    public void testRoutingSlipInvalidEndpoint() throws Exception {
        context.addRoutes(new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                from("direct:start")
                    .routingSlip(header("slip")).ignoreInvalidEndpoints();  // ← hides the bug
            }
        });

        getMockEndpoint("mock:result").expectedMessageCount(1);

        template.sendBodyAndHeader("direct:start", "Hello", "slip",
            "fail:endpoint,mock:result");

        assertMockEndpointsSatisfied();  // passes, but doesn't test error handler behavior
    }
}
```