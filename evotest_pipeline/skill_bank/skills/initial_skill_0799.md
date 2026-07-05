---
name: service-pool-memory-leak-on-stop
description: When a service pool caches producer instances and relies on route stops
  to release them, test that stopping and restarting a route does not cause a memory
  leak of producer references. This applies to SharedProducerServicePool, DefaultProducerServicePool,
  and DefaultServicePool patterns.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- RESOURCE_MANAGEMENT
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# service-pool-memory-leak-on-stop

## Instructions

# Service Pool Memory Leak on Stop

## Instructions

- WHEN the TG encounters a class that manages a pool or cache of producer/service instances (e.g., `SharedProducerServicePool`, `DefaultProducerServicePool`, `DefaultServicePool`) where instances are added upon usage and expected to be released upon stop/shutdown:
  - THEN the TG MUST write a test that repeatedly starts and stops a route (or the service pool) many times (e.g., 1000 iterations using a loop) and verifies that the number of cached/pooled instances does not grow without bound.
  - The test SHOULD create a `CamelContext` with a route that uses `to("direct:...")` or similar endpoint that triggers producer acquisition through the pool. After each iteration, stop the context, assert the pool size, and clean up.
  - The test MUST verify the pool size is as expected after many start/stop cycles (e.g., only 1 transient producer remains), not that all iterations have accumulated (e.g., 1000 producers).
  - Use `assertTrue(context.getRegistry().lookupByNameAndType("producerServicePool", SharedProducerServicePool.class).size() == expected)` or inject the pool and check its internal collection size (e.g., `pool.getProducers().size()` or `pool.getSize()`).
  - Common pitfalls:
    - Testing only a single usage without repeated start/stop cycles — this will NOT expose the leak.
    - Failing to stop the `CamelContext` between iterations — the leak only manifests when stop is called but resources are not released.
    - Using `Thread.sleep()` without proper synchronization — the pool operations may be async; use a `CountDownLatch` or assert after the context fully stops.
    - Assuming the test passes on the first iteration — the bug is cumulative and requires many cycles (e.g., 1000) to fail.

### Correct example (detects the leak):
```java
@Test
public void testForMemoryLeak() throws Exception {
    int size = 1000;
    for (int i = 0; i < size; i++) {
        CamelContext context = new DefaultCamelContext();
        context.addRoutes(new RouteBuilder() {
            @Override
            public void configure() throws Exception {
                from("direct:start").to("log:foo");
            }
        });
        context.start();
        context.stop();
    }
    SharedProducerServicePool pool = ...; // inject or lookup
    assertTrue("Expected one transient producer as service, but was: " + pool.size(), pool.size() == 1);
}
```

### Incorrect example (misses the leak):
```java
@Test
public void testSingleStartStop() throws Exception {
    CamelContext context = new DefaultCamelContext();
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:start").to("log:foo");
        }
    });
    context.start();
    context.stop();
    // Only checks one cycle — will never fail on this bug
    assertTrue(pool.size() <= 1);
}
```