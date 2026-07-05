---
name: seda-queue-reference-lifecycle
description: When testing SedaComponent or VmEndpoint with route lifecycle operations
  (stop/remove/add), the TG should test that QueueReference counts are properly cleaned
  up and re-initialized upon route re-addition, preventing stale queue references
  from blocking message delivery.
code_tags:
- NULL_CHECK
- VALIDATION
- EXCEPTION_HANDLING
- QUEUE_REFERENCE_MANAGEMENT
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# seda-queue-reference-lifecycle

## Instructions

# Seda Queue Reference Lifecycle After Route Removal and Re-addition

## Instructions

- WHEN the TG encounters SedaComponent.getQueue() returning an existing QueueReference from the queues map, and the route is subsequently stopped and removed
- THEN the TG should write a test that:
  1. Creates a route using a seda endpoint (e.g., "seda:foo")
  2. Starts the route and sends a message, verifying it arrives at the consumer
  3. Stops and removes the route from the CamelContext
  4. Re-adds the **same route** (same endpoint URI) to the context
  5. Starts the new route and sends a message, verifying it arrives at the consumer
  6. Expects the message count to be exactly 1 (not 0 or 2)
- The TG should verify that after route re-creation, the SedaEndpoint creates a fresh consumer that attaches to the queue, and that exchanges sent after re-creation are properly consumed. The bug occurs because QueueReference retains a ref count or reference to the old queue consumer, causing the new consumer to not receive messages on the re-added route.
- Common pitfalls to avoid:
  - Testing only the first route creation (without remove/add cycle) — this passes on both buggy and fixed versions
  - Using different endpoint URIs after re-addition — the bug only manifests when the **same** URI is re-used
  - Forgetting to use MockEndpoint.setExpectedMessageCount(1) and assertIsSatisfied() after both the first and second route deployments
  - Assuming the SedaEndpoint will automatically clean up its reference when the route is removed — it does not in the buggy version

### Correct example (catches the bug):

```java
public void testRemoveRouteAndThenAddItAgain() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:out");
    mock.expectedMessageCount(1);

    template.sendBody("seda:foo", "A");

    mock.assertIsSatisfied();
    mock.reset();

    // stop and remove the route
    context.stopRoute("foo");
    context.removeRoute("foo");

    // re-create the same route
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("seda:foo").to("mock:out");
        }
    });
    context.startRoute("foo");

    // Send another message after re-creation
    MockEndpoint mock2 = getMockEndpoint("mock:out");
    mock2.expectedMessageCount(1);

    template.sendBody("seda:foo", "B");

    mock2.assertIsSatisfied();
}
```

### Incorrect example (fails to catch the bug):

```java
public void testOnlyFirstRoute() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:out");
    mock.expectedMessageCount(1);
    template.sendBody("seda:foo", "A");
    mock.assertIsSatisfied();
    // Never tests the remove/add cycle — passes on buggy version
}
```