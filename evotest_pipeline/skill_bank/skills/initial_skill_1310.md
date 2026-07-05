---
name: vm-multiple-consumers-concurrent-route
description: When testing a VM (or SEDA/Disruptor) endpoint with multiple consumers
  from different contexts/routes, verify that the endpoint correctly creates separate
  consumer queues for each context instead of sharing state. Use this to catch bugs
  where concurrent route startup leads to shared consumer state and lost messages.
code_tags:
- CONCURRENCY
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# vm-multiple-consumers-concurrent-route

## Instructions

# VM Multiple Consumers Concurrent Route Test

## Instructions

- WHEN the TG encounters a Camel `vm:` (or `seda:`, `disruptor:`) endpoint that uses `?multipleConsumers=true` and the test creates consumers from **different Camel contexts** or from **different routes within the same context**
- THEN the TG should write an integration test that:
  1. Creates **two separate `CamelContext` instances** (e.g., `context1` and `context2`) that share a `VmComponent` in the `Registry`
  2. In one context (`context1`), starts a route that sends messages to a `vm:foo` endpoint at a fixed interval (e.g., using a `timer` or direct producer)
  3. In the second context (`context2`), starts **two routes** consuming from the same `vm:foo?multipleConsumers=true`, each routing to a separate mock endpoint (e.g., `mock:route1` and `mock:route2`)
  4. Sends a sufficient number of messages (e.g., 10) and verifies that **both** mock endpoints receive all messages (e.g., `mock.expectedMessageCount(10)` on each)
  5. **Starts the consumer contexts first**, then the producer context, to prevent race conditions from masking the bug
  6. Sets reasonable timeout values (e.g., `mock.setResultWaitTime(5000)`) to catch cases where messages are only delivered to one consumer

- **Common pitfalls to avoid:**
  - Starting contexts in the wrong order (consumers must start before producers)
  - Using only a single `CamelContext` — the bug manifests specifically when consumers come from different contexts that share a `VmComponent` registry
  - Not setting a timeout on mock assertions, causing the test to hang instead of fail
  - Testing with only one consumer per endpoint — the bug requires at least two consumers registered simultaneously
  - Using `seda:` instead of `vm:` — while similar, `seda:` does not use a shared component registry across contexts

- **Correct example (what the TG should write):**
  ```java
  @Test
  public void testVmMultipleConsumersRemoteRoute() throws Exception {
      Registry registry = new SimpleRegistry();
      VmComponent vm = new VmComponent();
      vm.setCamelContext(context1); // share component across contexts
      registry.bind("vm", vm);
      
      CamelContext context1 = new DefaultCamelContext(registry);
      context1.addRoutes(new RouteBuilder() {
          @Override
          public void configure() {
              from("direct:start").to("vm:foo");
          }
      });
      
      CamelContext context2 = new DefaultCamelContext(registry);
      MockEndpoint mock1 = context2.getEndpoint("mock:route1", MockEndpoint.class);
      MockEndpoint mock2 = context2.getEndpoint("mock:route2", MockEndpoint.class);
      mock1.expectedMessageCount(10);
      mock2.expectedMessageCount(10);
      mock1.setResultWaitTime(5000);
      mock2.setResultWaitTime(5000);
      
      context2.addRoutes(new RouteBuilder() {
          @Override
          public void configure() {
              from("vm:foo?multipleConsumers=true").routeId("route1").to("mock:route1");
              from("vm:foo?multipleConsumers=true").routeId("route2").to("mock:route2");
          }
      });
      
      context2.start();  // consumers start first
      context1.start();  // producer starts after consumers are registered
      
      for (int i = 0; i < 10; i++) {
          template.sendBody("direct:start", "message " + i);
      }
      
      assertMockEndpointsSatisfied();
  }
  ```

- **Incorrect example (what the TG might wrongly do):**
  ```java
  // WRONG: Single context, no shared VM component, wrong startup order
  @Test
  public void testVmMultipleConsumers() throws Exception {
      CamelContext context = new DefaultCamelContext();
      context.addRoutes(new RouteBuilder() {
          @Override
          public void configure() {
              from("direct:start").to("vm:foo");
              from("vm:foo?multipleConsumers=true").to("mock:route1");
              from("vm:foo?multipleConsumers=true").to("mock:route2");
          }
      });
      context.start();
      // This won't catch the bug because all consumers are in one context
  }
  ```