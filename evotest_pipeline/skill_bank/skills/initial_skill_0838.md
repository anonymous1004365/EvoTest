---
name: advicewith-on-exception-route-mutation
description: When using adviceWith to modify routes that contain onException clauses,
  tests must ensure the weaving process correctly handles exception handlers. This
  skill helps detect bugs where onException handlers are lost or improperly matched
  after adviceWith operations.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# advicewith-on-exception-route-mutation

## Instructions

# Testing adviceWith Route Interception with onException Handlers

## Instructions

**WHEN** the test uses `RouteDefinition.adviceWith()` to modify a route (via `AdviceWithRouteBuilder` such as `weaveByType().remove()`, `weaveAddFirst()`, `interceptSendToEndpoint()`, etc.) **AND** the route contains `onException` clauses that handle specific exception types,

**THEN** the test MUST:

1. **Weave around the onException handler**: Use `weaveByType().select(OnExceptionDefinition.class)` to target onException processors and verify they survive the adviceWith operation. Verify that after weaving, onException clauses still match and handle the expected exceptions.

2. **Test exception handling after weaving**: Send messages that trigger the onException clause on the modified route and assert that the exception IS still handled (e.g., the exchange is not failed, the expected error handling occurs). On the buggy version, the onException clause may be silently removed or lost during adviceWith, causing the exception to propagate unhandled (e.g., `IllegalArgumentException` from `DefaultErrorHandler` or `RuntimeCamelException`).

3. **Cover multiple onException scenarios**: If the route has multiple `onException` clauses for different exception types, test at least the most general one (e.g., `Exception.class`) to ensure it is not lost during weaving.

4. **Verify error handler state post-weaving**: After `adviceWith()`, inspect or assert that `ExchangePattern.InOut` and error handler behavior matches the original route's intent. The bug occurs when the onException is removed but the route is modified, leaving the exchange's error handler in an inconsistent state.

**Common pitfalls to avoid:**
- Testing only the happy path (message flows normally) without testing exception paths post-adviceWith
- Assuming onException handlers are preserved across adviceWith without explicit verification
- Using `mock:end` or similar endpoints without also verifying that onException handlers still route to their expected destinations
- Not testing that the correct exception type is still caught by the onException clause (e.g., testing with a different exception type than what is configured)

**Correct example** (this test catches the bug):
```java
// Test that after adviceWith with weaveAddFirst and weaveByType().remove(),
// the onException(Exception.class) handler still catches exceptions
context.getRouteDefinitions().get(0).adviceWith(context, new AdviceWithRouteBuilder() {
    @Override
    public void configure() throws Exception {
        weaveByType().select(OnExceptionDefinition.class).remove();
        weaveAddFirst().to("mock:a");
    }
});
context.start();

template.sendBody("direct:start", "Hello World");
// Expect: the onException is LOST — exception propagates → route fails
```

**Incorrect example** (does not catch the bug):
```java
// Only testing the normal message flow after adviceWith
context.getRouteDefinitions().get(0).adviceWith(context, new AdviceWithRouteBuilder() {
    @Override
    public void configure() throws Exception {
        weaveAddFirst().to("mock:a");
    }
});
context.start();

// Only verifies the mock:a was called, but never triggers onException
MockEndpoint mock = context.getEndpoint("mock:a", MockEndpoint.class);
mock.expectedMessageCount(1);
template.sendBody("direct:start", "Hello World");
mock.assertIsSatisfied();
```