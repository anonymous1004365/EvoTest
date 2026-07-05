---
name: route-suspend-impacts-error-handler-resume
description: When stopping/suspending a route that shares an error handler (e.g.,
  DeadLetterChannel) with other routes, the error handler's lifecycle (suspend/resume)
  may be incorrectly tied to individual route lifecycle events. The TG should verify
  that stopping a route does not permanently disable the error handler for other still-running
  routes.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- NULL_CHECK
- ROUTE_LIFECYCLE
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: STATE_TEST
---

# route-suspend-impacts-error-handler-resume

## Instructions

# Route Suspend Impacts Error Handler Resume

## Instructions

- **WHEN** the test involves calling `CamelContext.stopRoute(String routeId)` or `context.suspendRoute(String routeId)` on one route while other routes are still running, and those routes share a `DeadLetterChannel` or any per-context error handler (e.g., `errorHandler(deadLetterChannel("mock:dead"))`)
- **THEN** the TG must also verify that the remaining running routes still deliver messages to the error handler (e.g., `mock:dead`) after the first route is stopped/suspended. The test should:
  1. Set up at least two routes (e.g., `route1` and `route2`) using `errorHandler(deadLetterChannel("mock:dead"))`
  2. Send a message to `route1` to confirm the error handler works (e.g., send a message that causes an exception; verify `mock:dead` receives it)
  3. Stop/suspend `route1` using `context.stopRoute("route1")` or `context.suspendRoute("route1")`
  4. Send a message to `route2` that also causes an exception
  5. Verify that `mock:dead` still receives the message from `route2` — on the buggy version, the error handler would have been shut down during `route1`'s stop, and messages from `route2` would not reach the dead letter channel.
- **Common pitfalls**:
  - ❌ Testing only that `stopRoute` works without verifying the error handler still functions for remaining routes
  - ❌ Using separate error handler instances per route (the bug only manifests when routes share a single error handler, typically via `errorHandler(...)` at the `CamelContext` level)
  - ❌ Not causing an actual exception in the second route's message processing (the error handler must be triggered by a thrown exception)
  - ❌ Forgetting to wait for the route to fully stop before sending messages to the other route
- **Correct example**:
```java
// Setup
context.addRoutes(new RouteBuilder() {
    @Override
    public void configure() throws Exception {
        errorHandler(deadLetterChannel("mock:dead"));

        from("direct:start1").routeId("route1")
            .throwException(new IllegalArgumentException("Fail1"));

        from("direct:start2").routeId("route2")
            .throwException(new IllegalArgumentException("Fail2"));
    }
});
context.start();

// Verify both routes can use error handler
template.sendBody("direct:start1", "test");
mockDead.assertIsSatisfied(); // message received

// Stop route1
context.stopRoute("route1");
mockDead.reset();

// Send to route2 — error handler should still work
template.sendBody("direct:start2", "test again");
mockDead.assertIsSatisfied(); // FAILS on buggy version
```
- **Common pitfalls example**:
```java
// ❌ WRONG: Only tests that stopRoute works, doesn't test error handler after stop
context.stopRoute("route1");
// No verification of error handler for other routes

// ❌ WRONG: Uses per-route error handlers (won't trigger the sharing bug)
from("direct:start1").routeId("route1")
    .errorHandler(deadLetterChannel("mock:dead1"))
    .throwException(new IllegalArgumentException("Fail"));

from("direct:start2").routeId("route2")
    .errorHandler(deadLetterChannel("mock:dead2"))
    .throwException(new IllegalArgumentException("Fail"));
```