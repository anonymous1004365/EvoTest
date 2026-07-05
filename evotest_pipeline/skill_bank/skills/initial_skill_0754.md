---
name: recipient-list-parallel-aggregate-concurrency
description: When testing recipient list or multicast processors with parallelProcessing
  and parallelAggregate, verify that the aggregateExecutorService is properly shut
  down after completion to avoid thread leaks and hung test executions.
code_tags:
- CONCURRENCY
test_pattern: PERFORMANCE_TEST
---

# recipient-list-parallel-aggregate-concurrency

## Instructions

# Recipient List Parallel Aggregate Concurrency Test

## Instructions

- WHEN the TG encounters a `RecipientListProcessor` or `MulticastProcessor` that uses `parallelProcessing().parallelAggregate()` with a custom thread pool or a default thread pool profile
- THEN the TG should write a performance/stress test that:
  1. Creates a route with `recipientList` or `multicast` using `.parallelProcessing().parallelAggregate()` and an `AggregationStrategy`
  2. Sends a large batch of messages (e.g., 100-200 messages) through the route
  3. Uses a mock endpoint to collect results and assert that all messages were received (e.g., `mock.expectedMessageCount(N)`)
  4. Verifies that the test completes within a reasonable timeout (e.g., 30 seconds) and does **not** hang due to aggregateExecutorService threads not being reclaimed
  5. Asserts that the aggregateExecutorService is properly shut down after route stops (if accessible) — or more practically, verifies that the test thread pool executor does not leak threads by checking that the JVM does not retain daemon threads from the aggregate executor
- Common pitfalls:
  - Testing only with small message counts (e.g., 1-5) which may not trigger the concurrency issue
  - Not setting a timeout on the mock endpoint, causing the test to hang indefinitely if the aggregate executor hangs
  - Forgetting to use `.parallelAggregate()` which is the specific trigger for the separate aggregate executor thread pool
- Correct example:

```java
@Test
public void testRecipientListParallelAggregateWithManyMessages() {
    RouteBuilder routeBuilder = new RouteBuilder() {
        @Override
        public void configure() {
            from("direct:start")
                .recipientList(constant("mock:a,mock:b,mock:c"))
                .parallelProcessing()
                .parallelAggregate()
                .aggregationStrategy(new MyAggregationStrategy())
                .to("mock:result");
        }
    };
    
    context.addRoutes(routeBuilder);
    context.start();
    
    MockEndpoint mockResult = getMockEndpoint("mock:result");
    mockResult.expectedMessageCount(100);
    
    for (int i = 0; i < 100; i++) {
        template.sendBody("direct:start", "message-" + i);
    }
    
    mockResult.assertIsSatisfied(30000); // 30 second timeout
}
```

- Incorrect example (missing `.parallelAggregate()` and too few messages):

```java
@Test
public void testRecipientListBasic() {
    from("direct:start")
        .recipientList(constant("mock:a,mock:b"))
        .to("mock:result");  // No parallelProcessing, no parallelAggregate
    
    // This test would pass even on the buggy version and does not exercise the concurrency issue
}
```