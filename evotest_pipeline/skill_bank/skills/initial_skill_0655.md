---
name: on-exception-when-simple-ognl-validation
description: When using onException().when() with Simple language expressions that
  contain OGNL-like property references (e.g., ${exception.message}), tests must verify
  that the expression evaluates correctly on the caught exception and does not cause
  routing failures.
code_tags:
- NULL_CHECK
- EXCEPTION_HANDLING
- VALIDATION
test_pattern: INTERACTION_TEST
---

# on-exception-when-simple-ognl-validation

## Instructions

# OnException When Simple OGNL Validation

## Instructions

- WHEN the TG encounters a route that uses `onException(SomeException.class).when("${exception.property}")` with a Simple language expression that references properties on the caught exception instance (e.g., `${exception.message}`, `${exception.code}`)
- THEN the TG should write an integration test that:
  1. Creates a route that throws the expected exception in a processor or from a service call
  2. Uses `.onException(SomeException.class).when(simple("${exception.property} == expectedValue")).handled(true).to("mock:handled")` in the route
  3. Sends a message to the route that triggers the exception
  4. Asserts that the exchange ends up at `mock:handled` (the exception was caught and handled correctly)
  5. Asserts that the `mock:handled` endpoint received exactly 1 exchange
  6. Verifies no unhandled exceptions propagate out of the route

- Include a negative test case where the Simple condition does NOT match (e.g., `${exception.property} == wrongValue`), and verify the exception is NOT handled and propagates out.

- Common pitfalls to avoid:
  - Testing only that an exception is thrown, without verifying the `when()` condition filtering works correctly
  - Forgetting that `${exception.property}` in Simple language refers to the caught exception object on the Exchange's `Exception` property, not a header
  - Not testing the negative case (condition that should NOT match)
  - Assuming OGNL-style property access (`exception.message`) works the same as method invocation — test uses actual property names

- CORRECT test pattern:
```java
public class OnExceptionWhenSimpleOgnlTest extends CamelTestSupport {
    @Test
    public void testOnExceptionWhenSimpleOgnl() throws Exception {
        getMockEndpoint("mock:handled").expectedMessageCount(1);
        template.sendBody("direct:start", "Hello World");
        assertMockEndpointsSatisfied();
    }
    
    protected RouteBuilder createRouteBuilder() throws Exception {
        return new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                onException(Exception.class)
                    .when(simple("${exception.message} contains 'test'"))
                    .handled(true)
                    .to("mock:handled");
                    
                from("direct:start")
                    .throwException(new IllegalArgumentException("test exception"));
            }
        };
    }
}
```

- INCORRECT pattern (missing negative case, missing assertion on mock):
```java
// INCORRECT — only tests that a route exists, doesn't verify behavior
@Test
public void testOnExceptionWhenSimpleOgnl() throws Exception {
    template.sendBody("direct:start", "Hello World");
}
```