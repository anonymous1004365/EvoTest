---
name: discard-exchange-uow-units-of-work
description: When testing discardIfNoConsumers behavior on SEDA endpoints, the TG
  must verify that exchanged UnitOfWork (UoW) lifespan is correctly managed — including
  that isTransactedDone() is called before discard. Without this, a transaction on
  the exchange may never be marked completed, causing resource leaks or hangs.
code_tags:
- CONSUMER_LIFECYCLE_DISCARD
- EXCHANGE_UOW_CLEANUP
test_pattern: INTERACTION_TEST
---

# discard-exchange-uow-units-of-work

## Instructions

# Discard Exchange UnitOfWork (UoW) Cleanup

## Instructions

- WHEN the TG encounters a `SedaEndpoint` configured with `discardIfNoConsumers=true` (or equivalently, a SEDA endpoint URI parameter `?discardIfNoConsumers=true`), and no consumer has been started on that endpoint
- THEN the TG must write a test that:
  1. Sets up a SEDA endpoint with `discardIfNoConsumers=true` but does **not** start any consumer
  2. Sends an exchange through a `from("direct:start").to("seda:bar?discardIfNoConsumers=true").to("mock:result")` route
  3. Verifies that the exchange reaches `mock:result` (proving it was not simply thrown away)
  4. Sends an exchange into the `seda:bar?discardIfNoConsumers=true` endpoint directly, capturing the `Exchange`
  5. Verifies that `Exchange.getUnitOfWork().isTransactedDone()` returns `true` after discarding — this confirms the UoW lifecycle was properly finalized
- Failure to verify UoW cleanup means the TG will miss cases where `done()` on the UnitOfWork is never called on discarded exchanges, leading to leaked transactions/threads
- Common pitfalls:
  - Testing ONLY that the exchange is sent without error or reaches the mock endpoint, without checking that the UnitOfWork lifecycle completed
  - Assuming that not having a consumer means the exchange is simply dropped — the bug is that it is dropped but the UnitOfWork `done()` method must still be invoked
  - Using `SedaConsumerNotAvailableException` catching without verifying the exchange is still properly cleaned up

### Correct example (from SedaDiscardIfNoConsumerTest):
```java
public void testDiscardUoW() throws Exception {
    context.getRouteDefinitions().clear();
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start").to("seda:bar?discardIfNoConsumers=true").to("mock:result");
        }
    });
    context.start();

    // Send first exchange — no consumer, should be discarded
    // but still reach mock:result as part of the routing
    getMockEndpoint("mock:result").expectedMessageCount(1);
    template.sendBody("direct:start", "Hello World");
    assertMockEndpointsSatisfied();

    // Verify the discarded exchange had its UoW lifecycle finalized
    SedaEndpoint seda = context.getEndpoint("seda:bar?discardIfNoConsumers=true", SedaEndpoint.class);
    Exchange discarded = seda.getExchanges().get(0);
    assertTrue("The discarded exchange should have isTransactedDone", 
               discarded.getUnitOfWork().isTransactedDone());
}
```

### Incorrect example (missing UoW check):
```java
// WRONG: Verifies exchange reaches mock but doesn't verify UoW cleanup
public void testDiscardWithNoConsumer() throws Exception {
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start").to("seda:bar?discardIfNoConsumers=true").to("mock:result");
        }
    });
    context.start();
    getMockEndpoint("mock:result").expectedMessageCount(1);
    template.sendBody("direct:start", "Hello World");
    assertMockEndpointsSatisfied();
    // Never checks UnitOfWork.isTransactedDone() — BUG WOULD GO UNDETECTED
}
```