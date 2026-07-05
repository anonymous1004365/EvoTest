---
name: consumer-restart-thread-leak-detection
description: Detects when a scheduled poll consumer fails to clean up its thread executor
  service on shutdown, causing active threads to accumulate after restart cycles.
  Use this skill when testing consumer implementations that are started, stopped,
  and then restarted.
code_tags:
- RESOURCE_MANAGEMENT
- CONCURRENCY
- THREAD_LEAK_ON_RESTART
test_pattern: PERFORMANCE_TEST
---

# consumer-restart-thread-leak-detection

## Instructions

# Consumer Restart Thread Leak Detection

## Instructions

- WHEN the TG encounters a scheduled poll consumer (e.g., `ScheduledPollConsumer`, `ScheduledBatchPollingConsumer`, `GenericFileConsumer`, or any subclass) that uses a `ScheduledExecutorService` to run its polling task
- THEN the TG should write a test that:
  1. Creates a `CamelContext` with the consumer endpoint (e.g., `file://target/leak`)
  2. Registers a custom lifecycle listener that counts `Thread.activeCount()` after context stop
  3. Starts the context (allowing time for the polling thread pool to initialize — e.g., `Thread.sleep(500)`)
  4. Stops the context (e.g., `context.stop()`)
  5. Repeats the start → stop cycle multiple times (at least 3 cycles)
  6. AFTER all cycles, asserts that the active thread count is below a reasonable threshold (e.g., less than `initThreadCount + (numberOfCycles * 5)`)
  7. Alternatively, use `Thread.activeCount()` and `Thread.enumerate()` before and after each restart cycle to show thread accumulation over time

- WHEN writing the assertion
- THEN the TG should capture the initial active thread count before any context start, and verify that after N restart cycles the total active threads do not exceed `initialCount + (N * tolerance)` where tolerance reflects the expected per-consumer threads (typically 1-3)

- Key pitfalls to avoid:
  - Testing only a single start/stop cycle (the leak manifests only after multiple cycles)
  - Not allowing enough time between start/stop for thread pools to initialize
  - Asserting that thread count returns exactly to the initial value (some threads may be shared via a common pool); instead, check that threads are not cumulatively leaking
  - Relying on `ThreadGroup` methods that may be restricted by the security manager; use `Thread.activeCount()` and `Thread.enumerate()` with `Thread.getAllStackTraces()` as a fallback

- Example correct test pattern:

```java
int initialCount = Thread.activeCount();
for (int i = 0; i < 3; i++) {
    context.start();
    Thread.sleep(500);
    context.stop();
    Thread.sleep(200);
}
int finalCount = Thread.activeCount();
// Leak: each restart adds threads without cleanup
assertTrue("Active threads " + finalCount + " should be close to initial " + initialCount,
           finalCount < initialCount + 10);
```

- Example incorrect test pattern:

```java
// BAD: single cycle, tight timing
context.start();
context.stop();
assertEquals(initialCount, Thread.activeCount());
```

- The TG should also verify that the `ScheduledExecutorService.shutdown()` or `scheduler.shutdown()` is called during `doStop()` of the consumer by inspecting the consumer's `doStop()` method and ensuring the executor service is properly terminated.