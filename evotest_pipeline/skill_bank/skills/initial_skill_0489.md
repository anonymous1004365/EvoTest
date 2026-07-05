---
name: routing-slip-producer-null-safety
description: When testing route definitions involving routing slip endpoints with
  custom URI parameters (like ?createProducer=true), the TG should test that the routing
  slip correctly handles producer creation failures by verifying the exchange counter
  value. Use this skill when a RoutingSlip endpoint uses a custom parameter that influences
  how producers are created per message.
code_tags:
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# routing-slip-producer-null-safety

## Instructions

# Routing Slip Producer Null Safety

## Instructions

- WHEN the TG encounters a Route definition where routing slip endpoints use custom URI parameters (e.g., `?createProducer=true`) that affect how producers are created or reused
- THEN the TG should write a test that:
  1. Creates a Route where the routing slip's middle endpoint (the one with `&producer=true` or similar parameter) forces a producer creation failure — e.g., by using a URI that causes `createProducer` to fail
  2. Sends a message to the route and asserts that the exchange counter (the number of times the exchange was processed through the routing slip) is **0** (not 1) — because if the producer creation failed, the exchange should not have been counted as processed
  3. The test should verify that when `createProducer` is set on a routing slip endpoint URI, a failure to create that producer results in the exchange's counter being at zero (i.e., the message is not forwarded/processed)
- Common pitfalls to avoid:
  - Testing only happy path scenarios where all endpoints succeed
  - Assuming that `producer=true` endpoints will always succeed and the counter will always increment
  - Not checking the exchange property/header that tracks routing slip processing count (e.g., `CamelSlipCounter`, `Exchange.SLIP_ENDPOINT`, or similar counter property)
  - Not using a URI that explicitly fails producer creation to trigger the edge case

### Incorrect Example (misses the bug)
```java
// Sends message, only checks no exception, does NOT check counter
template.sendBody("direct:start", "Hello");
assertMockEndpointsSatisfied();
```

### Correct Example (catches the bug)
```java
// Sends message and checks exchange counter is 0 after producer creation failure
Exchange exchange = template.send("direct:start", new Processor() {
    public void process(Exchange exchange) throws Exception {
        exchange.getIn().setBody("Hello");
    }
});
// The routing slip endpoint had ?createProducer=true and failed; counter should be 0
assertEquals(0, exchange.getProperty(Exchange.SLIP_COUNTER, Integer.class).intValue());
```