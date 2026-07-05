---
name: route-scoped-on-exception-with-intercept-send
description: When a route uses interceptSendToEndpoint combined with route-scoped
  onException, the TG should test that both route-scoped exception handlers (with
  predicates) and interceptSendToEndpoint work together without causing NullPointerException.
  The test should verify that intercepting endpoints does not break onException clauses
  that have predicates.
code_tags:
- ADVICE_WITH_ROUTE_INTERCEPTION
test_pattern: INTERACTION_TEST
---

# route-scoped-on-exception-with-intercept-send

## Instructions

# Route-Scoped onException with interceptSendToEndpoint Interaction

## Instructions

- WHEN the TG encounters a test case that uses `adviceWith` to replace or mock endpoints (such as `mock:foo` replacing `direct:bar`) via `interceptSendToEndpoint`, AND the route(s) being tested have **route-scoped** `onException` clauses (defined via `onException(...)` inside the route builder, not as a global exception handler) — especially those with predicates (e.g., `.onException(SomeException.class).onWhen(header("someHeader").isEqualTo("someValue"))`)
- THEN the TG should write a test that exercises the **full interaction** between the intercept and the exception handler. Specifically:
  1. Set up a route with a route-scoped `onException` clause that has a predicate.
  2. Use `interceptSendToEndpoint("direct:...").skipSendToOriginalEndpoint().to("mock:...")` or equivalent in the test to intercept an endpoint that the route sends to.
  3. Send a message that **triggers the onException clause** (i.e., throws the exception that the onException handles) to verify the exception handler works correctly when intercept is active.
  4. Also send a message that does **not** trigger the exception to verify the intercept works correctly.
  5. The test should verify that **no NullPointerException** is thrown during route processing — especially during endpoint interception when an exchange property like `Exchange.INTERCEPTED_ENDPOINT` is being resolved.
- Common pitfalls:
  - Testing interceptSendToEndpoint and onException in isolation rather than together, missing the interaction bug.
  - Using only global onException (via `getContext().onException(...)`) when the bug specifically involves route-scoped onException.
  - Forgetting to add `.skipSendToOriginalEndpoint()` when mocking endpoints, which can cause the original endpoint to still be called.
  - Not including a predicate on the onException clause, which is a key trigger for this bug pattern.
- Example correct test (Java with CamelTestSupport):

```java
// CORRECT: Tests interaction of interceptSendToEndpoint and route-scoped onException with predicate
public class InterceptOnExceptionTest extends CamelTestSupport {
    @Override
    protected RoutesBuilder createRouteBuilder() throws Exception {
        return new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                onException(MyException.class)
                    .onWhen(header("foo").isEqualTo("bar"))
                    .handled(true)
                    .transform(constant("handled"));
                
                from("direct:start")
                    .to("direct:intercepted");
            }
        };
    }
    
    @Test
    public void testInterceptWithOnException() throws Exception {
        // Use adviceWith to intercept
        context.getRouteDefinitions().get(0).adviceWith(context, new AdviceWithRouteBuilder() {
            @Override
            public void configure() throws Exception {
                interceptSendToEndpoint("direct:intercepted")
                    .skipSendToOriginalEndpoint()
                    .to("mock:intercepted");
            }
        });
        
        // This should trigger the onException with predicate
        // Without the fix, this causes NPE
        template.sendBodyAndHeader("direct:start", "test", "foo", "bar");
        
        // Verify the mock was called (intercept works)
        getMockEndpoint("mock:intercepted").expectedMessageCount(1);
        assertMockEndpointsSatisfied();
    }
}
```

- Example incorrect test:

```java
// WRONG: This tests interceptor in isolation without onException
// Does NOT trigger the interaction bug
public class InterceptOnlyTest extends CamelTestSupport {
    @Override
    protected RoutesBuilder createRouteBuilder() throws Exception {
        return new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                from("direct:start")
                    .to("direct:intercepted");
            }
        };
    }
    
    @Test
    public void testIntercept() throws Exception {
        context.getRouteDefinitions().get(0).adviceWith(context, new AdviceWithRouteBuilder() {
            @Override
            public void configure() throws Exception {
                interceptSendToEndpoint("direct:intercepted")
                    .skipSendToOriginalEndpoint()
                    .to("mock:intercepted");
            }
        });
        
        // This works fine even with the bug - onException is not involved
        template.sendBody("direct:start", "test");
        getMockEndpoint("mock:intercepted").expectedMessageCount(1);
        assertMockEndpointsSatisfied();
    }
}
```