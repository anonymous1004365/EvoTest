---
{}
---

---
name: vm-seda-multiple-consumers-queue-consistency
description: WHEN a VmComponent (or SedaComponent) uses shared queues across CamelContexts with multipleConsumers=true, THEN a test must verify that consumers on different VM endpoints with different names do NOT share the same queue and do NOT interfere with each other. The test should set up consumers on different vm: URIs and verify that messages sent to one endpoint do not leak into another endpoint's queue.
code_tags: ['CLONE_AWARE_MERGE', 'STATE_MUTATION', 'ORDER_DEPENDENCY', 'CONCURRENCY']
test_pattern: STATE_TEST
---

# vm-seda-multiple-consumers-queue-consistency

## Instructions

# VM/SEDA Multiple Consumers Queue Isolation

## Instructions

- WHEN a test involves VmEndpoint or SedaEndpoint with `multipleConsumers=true` AND multiple CamelContext instances consuming from different VM endpoint URIs (e.g., `vm:producer` vs `vm:foo`)
- THEN the test should verify that consumers on different VM URIs are fully isolated and do NOT share a queue. For example, when two CamelContexts each consume from different VM endpoints (`vm:producer` vs `vm:foo`), sending 100 messages to `vm:producer` should result in 100 messages on the `mock:route1` endpoint (the consumer of `vm:producer`) and 0 messages on the `mock:route2` endpoint (the consumer of `vm:foo`).
- The test should explicitly assert the expected message counts on each endpoint: 100 for the correct endpoint, 0 for the unrelated endpoint.
- Include the Java class `VmMultipleConsumersMultipleContextTest` from `camel-core/src/test/java/org/apache/camel/component/vm/` as a reference.
- Common pitfalls to avoid:
    - Assuming that different VM endpoint URIs automatically share or don't share a queue — test both scenarios (same URI = shared, different URI = isolated).
    - Only testing with a single CamelContext — the bug manifests only when multiple CamelContext instances are involved.
    - Not asserting the negative case (the unrelated endpoint should receive 0 messages).

### Example of a correct test approach:
```java
// Start context 1 consuming from vm:producer
CamelContext consumerContext1 = new DefaultCamelContext();
consumerContext1.addRoutes(new RouteBuilder() {
    @Override
    public void configure() throws Exception {
        from("vm:producer?multipleConsumers=true").routeId("route1").to("mock:route1");
    }
});
consumerContext1.start();

// Start context 2 consuming from a DIFFERENT endpoint vm:foo
CamelContext consumerContext2 = new DefaultCamelContext();
consumerContext2.addRoutes(new RouteBuilder() {
    @Override
    public void configure() throws Exception {
        from("vm:foo?multipleConsumers=true").routeId("route2").to("mock:route2");
    }
});
consumerContext2.start();

MockEndpoint route1Mock = consumerContext1.getEndpoint("mock:route1", MockEndpoint.class);
MockEndpoint route2Mock = consumerContext2.getEndpoint("mock:route2", MockEndpoint.class);
route1Mock.expectedMessageCount(100);
route2Mock.expectedMessageCount(0);  // key: should receive NOTHING

// Send 100 messages to vm:producer
for (int i = 0; i < 100; i++) {
    template.sendBody("vm:producer?multipleConsumers=true", i);
}

route1Mock.assertIsSatisfied();
route2Mock.assertIsSatisfied();
```

### Example of an incorrect test approach (missing the negative assertion):
```java
// BAD: only tests positive case, never verifies that route2 receives 0
route1Mock.expectedMessageCount(100);
route2Mock.expectedMessageCount(100);  // Wrong! route2 should have 0, not 100
```