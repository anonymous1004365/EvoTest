---
name: vm-queue-key-collision-across-contexts
description: When testing VmComponent (or similar Seda-based components) with multiple
  Camel contexts sharing the same queue name, verify that queues are isolated per
  CamelContext instance. Without proper queue key scoping, consumers from different
  contexts may steal messages from each other, causing message loss.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
test_pattern: INTERACTION_TEST
---

# vm-queue-key-collision-across-contexts

## Instructions

# Vm Queue Key Collision Across CamelContexts

## Instructions

- WHEN the TG encounters tests for `org.apache.camel.component.vm.VmComponent` (or `SedaComponent`) where **multiple CamelContext instances** are created and each context routes to/from the **same VM endpoint URI** (e.g., `vm://foo`)
- THEN the TG should design a test that:
  1. Creates **two separate CamelContext instances** (e.g., `context1` and `context2`).
  2. In each context, creates a route that sends messages **to the same VM endpoint URI** (e.g., `vm://queueA`).
  3. In each context, creates a **consumer** on that same VM URI that collects received messages (e.g., using a `MockEndpoint`).
  4. Sends a **known number of messages** (e.g., 100) from **each context** to the shared VM URI.
  5. Verifies that **each context's consumer receives exactly the number of messages sent by its own context** (i.e., consumer in context1 receives 100, consumer in context2 receives 100), and NOT a mix of messages from both contexts.
  6. Uses `context.getEndpoint("vm://queueA", Endpoint.class)` to obtain the endpoint within each context to ensure the right queue reference.
- The test should expect that **without proper queue key scoping by CamelContext**, messages from one context leak into the other context's consumer, causing **message count mismatches** (e.g., expected 100 but received 95, due to the second context's consumer stealing some messages).
- **Common pitfalls to avoid**:
  - Testing only a single CamelContext — the bug only manifests with **multiple contexts** using the same endpoint URI.
  - Using the same `CamelContext` for both producers and consumers on the same VM queue — the bug is about **cross-context** queue key collision.
  - Using `vm://` URIs that differ in path or parameters — the bug specifically occurs when the **exact same VM endpoint URI** is used in multiple contexts.
  - Forgetting to start both contexts before sending messages and to shut them down after the test.
  - Relying on timing/thread sleep — the test should use `MockEndpoint.assertIsSatisfied()` with appropriate timeouts to verify message counts deterministically.

- **Correct example** (what a good test looks like):
  ```java
  public void testVmMultipleConsumersDifferentEndpoints() throws Exception {
      CamelContext context1 = new DefaultCamelContext();
      CamelContext context2 = new DefaultCamelContext();
      
      context1.addRoutes(new RouteBuilder() {
          @Override
          public void configure() {
              from("direct:in1").to("vm://queueA");
          }
      });
      context2.addRoutes(new RouteBuilder() {
          @Override
          public void configure() {
              from("direct:in2").to("vm://queueA");
          }
      });
      
      MockEndpoint mock1 = context1.getEndpoint("vm://queueA", MockEndpoint.class);
      MockEndpoint mock2 = context2.getEndpoint("vm://queueA", MockEndpoint.class);
      mock1.expectedMessageCount(100);
      mock2.expectedMessageCount(100);
      
      context1.start();
      context2.start();
      
      for (int i = 0; i < 100; i++) {
          template1.sendBody("direct:in1", "message" + i);
          template2.sendBody("direct:in2", "message" + i);
      }
      
      mock1.assertIsSatisfied();
      mock2.assertIsSatisfied();
      
      context1.stop();
      context2.stop();
  }
  ```

- **Incorrect example** (what a naive test might look like — missing the cross-context collision):
  ```java
  public void testVmSingleContext() throws Exception {
      CamelContext context = new DefaultCamelContext();
      context.addRoutes(new RouteBuilder() {
          @Override
          public void configure() {
              from("direct:in").to("vm://queueA");
              from("vm://queueA").to("mock:out");
          }
      });
      context.start();
      MockEndpoint mock = context.getEndpoint("mock:out", MockEndpoint.class);
      mock.expectedMessageCount(100);
      for (int i = 0; i < 100; i++) {
          template.sendBody("direct:in", "message" + i);
      }
      mock.assertIsSatisfied(); // passes even on buggy version — single context doesn't trigger the collision
      context.stop();
  }
  ```