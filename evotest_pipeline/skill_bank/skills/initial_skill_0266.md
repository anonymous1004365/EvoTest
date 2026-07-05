---
name: vm-endpoint-cache-isolation-across-contexts
description: ''
code_tags:
- QUEUE_SHARING_ISOLATION
- ENDPOINT_CACHING
test_pattern: STATE_TEST
---

# vm-endpoint-cache-isolation-across-contexts

## Instructions

# VM Endpoint Cache Isolation Across CamelContexts

## Instructions

- WHEN the TG encounters a `VmComponent` (or a component that extends `SedaComponent`) that has a static `ENDPOINTS` map (`Map<String, VmEndpoint>`) and a static `QUEUES` map (`Map<String, QueueReference>`), AND the TG sees that `createEndpoint` caches endpoints via `ENDPOINTS.put(uri, answer)` returning the cached instance on subsequent lookups...

- THEN the TG should write a multi-CamelContext test that:
  1. Creates two separate `CamelContext` instances (using `new DefaultCamelContext()`).
  2. Adds routes to each context — the first context listening on URI `A` (e.g., `"vm:producer?multipleConsumers=true"`) and the second context listening on a **different** URI `B` (e.g., `"vm:foo?multipleConsumers=true"`).
  3. Sends 100 messages to URI `A` and verifies via `MockEndpoint` that: 
     - The consumer on URI `A` receives all 100 messages.
     - The consumer on URI `B` receives 0 messages (no cross-contamination).
  4. The test must start the first context, then start the second context, then send messages to ensure the cache is populated by the first context before the second context creates its endpoint.
  5. Expect on the buggy version: the consumer on URI `A` will receive fewer than 100 messages (e.g., 73) because the second context's consumer on URI `B` steals a reference to the same queue via the cached endpoint, receiving some of the messages intended for URI `A`.

- Common pitfalls to avoid:
  - ❌ Testing only with the same URI in both contexts — this does NOT expose the cache-based queue-sharing bug.
  - ❌ Using the same `CamelContext` for both consumers — the cache only causes cross-URI contamination when different contexts share the static `ENDPOINTS`/`QUEUES` maps.
  - ❌ Starting both contexts before sending messages — the bug depends on the endpoint cache being populated by the first context before the second context's endpoint is created.
  - ❌ Testing only with `seda:` endpoints — the static cache exists in `VmComponent`, not in `SedaComponent` (which has instance-level maps). The bug is specific to `vm:`.

- Correct example (Java, JUnit 4 style):
```java
public void testVmMultipleConsumersDifferentEndpoints() throws Exception {
    // First context - consumer on "vm:producer"
    CamelContext ctx1 = new DefaultCamelContext();
    ctx1.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("vm:producer?multipleConsumers=true").routeId("route1").to("mock:route1");
        }
    });
    ctx1.start();
    MockEndpoint mock1 = ctx1.getEndpoint("mock:route1", MockEndpoint.class);
    mock1.expectedMessageCount(100);

    // Second context - consumer on "vm:foo" (different URI)
    CamelContext ctx2 = new DefaultCamelContext();
    ctx2.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("vm:foo?multipleConsumers=true").routeId("route2").to("mock:route2");
        }
    });
    ctx2.start();
    MockEndpoint mock2 = ctx2.getEndpoint("mock:route2", MockEndpoint.class);
    mock2.expectedMessageCount(0);

    // Send to "vm:producer" - should only go to route1
    for (int i = 0; i < 100; i++) {
        template.sendBody("vm:producer?multipleConsumers=true", i);
    }

    mock1.assertIsSatisfied();  // Expected: 100, Buggy: ~73
    mock2.assertIsSatisfied();  // Expected: 0,   Buggy: ~27
}
```

- Incorrect example (does NOT expose the bug):
```java
public void testSameUriBothContexts() throws Exception {
    // Both consumers use "vm:producer" - this is expected to share the queue
    // and does NOT expose the caching bug
}
```