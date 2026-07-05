---
name: seda-queue-concurrent-shutdown-test
description: When testing SEDA endpoint lifecycle with concurrent producers and consumers,
  verify that the internal queue is properly drained and consumers complete processing
  before shutdown completes, without blocking producers indefinitely.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- CONCURRENCY
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# seda-queue-concurrent-shutdown-test

## Instructions

# SEDA Queue Concurrent Shutdown Test

## Instructions

- WHEN the TG encounters a SEDA endpoint where multiple producer threads send messages concurrently while the endpoint is being shut down (e.g., via `context.stop()` or `endpoint.stop()`)
- THEN it should write an INTERACTION_TEST that:
  1. Creates a SEDA endpoint with a known queue (e.g., `seda:testQueue`).
  2. Sets up a consumer route from that SEDA endpoint to a mock endpoint (e.g., `mock:result`).
  3. Starts the Camel context and waits for the route to be active.
  4. Launches multiple producer threads (at least 2) that each send a message to the SEDA endpoint (e.g., via `template.sendBody("seda:testQueue", "message-<n>")`).
  5. After a short delay (e.g., 100ms), calls `context.stop()` from the main test thread while producer threads are still sending.
  6. Waits for all threads to complete (join with a generous timeout, e.g., 10 seconds).
  7. Asserts that all messages sent before shutdown were received at the mock endpoint (within the mock's assertion timeout).
  8. Asserts that no exceptions were thrown from the producer threads (e.g., no `SedaConsumerNotAvailableException`, no `CamelExecutionException`, no `InterruptedException`).
- The test MUST verify that the internal queue is drained properly and that consumers are not killed mid-processing, but that new producers are also not accepted after shutdown.
- Common pitfalls to avoid:
  - Using a single producer thread: this may not trigger the race condition.
  - Starting the context after starting threads: the context must be started first so the consumer is ready.
  - Not using `CountDownLatch` or similar synchronization to ensure producers have started before shutdown begins.
  - Using `Thread.sleep()` alone without a latch: producers may finish before shutdown is attempted.
  - Forgetting to join producer threads: the test may exit before producers complete, missing failures.
  - Asserting only the mock endpoint received messages but not checking for exceptions from threads.

**Correct example (schematic):**
```java
@Test
public void testConcurrentProducersDuringShutdown() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    int messageCount = 10;
    mock.expectedMinimumMessageCount(messageCount);
    CountDownLatch startedProducers = new CountDownLatch(2);
    CountDownLatch shutdownLatch = new CountDownLatch(1);
    List<Exception> exceptions = new CopyOnWriteArrayList<>();
    
    // Producer threads
    Runnable producer = () -> {
        try {
            startedProducers.countDown();
            shutdownLatch.await();
            for (int i = 0; i < messageCount; i++) {
                template.sendBody("seda:testQueue", "message-" + i);
            }
        } catch (Exception e) {
            exceptions.add(e);
        }
    };
    
    Thread t1 = new Thread(producer);
    Thread t2 = new Thread(producer);
    t1.start();
    t2.start();
    
    startedProducers.await();
    context.stop();
    shutdownLatch.countDown();
    
    t1.join(10000);
    t2.join(10000);
    
    mock.assertIsSatisfied();
    assertTrue("Producer threads threw exceptions: " + exceptions, exceptions.isEmpty());
}
```

**Common mistake (too simplistic, may not catch the bug):**
```java
@Test
public void testShutdown() throws Exception {
    MockEndpoint mock = getMockEndpoint("mock:result");
    mock.expectedMessageCount(5);
    for (int i = 0; i < 5; i++) {
        template.sendBody("seda:testQueue", "message-" + i);
    }
    context.stop(); // No concurrent producers, no race condition
    mock.assertIsSatisfied();
}
```