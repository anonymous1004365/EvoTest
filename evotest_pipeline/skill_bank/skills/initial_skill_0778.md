---
name: seda-queue-error-handle-test
description: When testing SEDA endpoints with error handling and dead letter queues,
  test that messages rejected due to a full queue are routed to the dead letter channel.
  This skill catches bugs where SedaProducer silently drops messages when the queue
  is full and a consumer is not available.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# seda-queue-error-handle-test

## Instructions

# SEDA Queue Error Handling with Dead Letter Channel

## Instructions

- WHEN the TG encounters a SEDA endpoint configuration with a `size` parameter (limiting queue capacity), error handling (e.g., `errorHandler` or `deadLetterChannel`), and a route that produces messages to that SEDA endpoint
- THEN the TG should write a test that:
  1. Configures the SEDA endpoint with a small queue size (e.g., `seda:foo?size=2`)
  2. Sets the endpoint to block when full (e.g., `blockWhenFull=false` — explicitly NOT blocking, so the offer/poll pattern is used)
  3. Configures an error handler on the route that sends to a mock dead letter endpoint (e.g., `errorHandler(deadLetterChannel("mock:dlc"))`)
  4. Sends more messages than the queue can hold (e.g., sends 3 messages to a queue of size 2) WITHOUT a consumer running (so the queue fills up and the producer tries to add to a full queue)
  5. Verifies that the excess messages are routed to the dead letter channel (mock:dlc) and the messages that fit are processed normally
  6. Also verify that the correct number of messages end up in each destination (e.g., 2 processed normally, 1 in DLQ)

- The test should verify that when a SedaProducer's `addToQueue` method encounters a full queue and the consumer is not running (or has been stopped), the exchange is rejected and handled by the Camel error handler rather than being silently dropped

- Common pitfalls to avoid:
  - Only testing the happy path where the queue never fills up
  - Not setting a small enough queue size to trigger the rejection
  - Not stopping/removing the consumer so the queue fills up
  - Sending messages synchronously when the test requires timing-sensitive async behavior — use proper synchronization or a mock endpoint to verify message counts
  - Not configuring `blockWhenFull=false` (default is false for SEDA, but test should be explicit)

### Correct Example (Java-like pseudocode)

```java
public void testErrorHandle() throws Exception {
    context.getRoute("seda:foo"); // route with errorHandler(deadLetterChannel("mock:dlc"))
    
    getMockEndpoint("mock:dlc").expectedMessageCount(1);
    getMockEndpoint("mock:result").expectedMessageCount(2);
    
    // Send 3 messages, queue size is 2, consumer is not available
    template.sendBody("seda:foo", "A");
    template.sendBody("seda:foo", "B");
    template.sendBody("seda:foo", "C");
    
    assertMockEndpointsSatisfied();
    // Expected: 2 messages processed, 1 in DLQ
}
```

### Incorrect Example

```java
public void testHappyPath() throws Exception {
    // Only tests normal operation without filling the queue
    template.sendBody("seda:foo", "A");
    template.sendBody("seda:foo", "B");
    
    getMockEndpoint("mock:result").expectedMessageCount(2);
    assertMockEndpointsSatisfied();
    // Fails to test what happens when queue is full
}
```