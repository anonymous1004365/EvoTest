---
name: component-initialization-atomicity
description: When a component framework has an initialization lifecycle with `internalInitialize()`,
  `fireInitialize()`, and `onInitialize()` methods, test that initialization is atomic
  and concurrent-safe — a race condition between `get()` and `internalInitialize()`
  could skip initialization. Use this skill when testing component initialization
  lifecycle methods.
code_tags:
- CONCURRENCY
- ORDER_DEPENDENCY
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# component-initialization-atomicity

## Instructions

# Test Atomicity of Component Initialization

## Instructions

- WHEN the TG encounters a component framework where initialization is triggered by calling a method like `internalInitialize()` (which internally calls `fireInitialize()` and then `onInitialize()`), and the component's initialized state is tracked by a boolean flag (e.g., `private boolean initialized = false`)
- THEN the TG should write a **concurrent test** that verifies two threaded calls to `internalInitialize()` result in `onInitialize()` being called exactly once, not zero times and not twice
- The test should:
  1. Create a component that overrides `onInitialize()` to record how many times it was called (e.g., via an `AtomicInteger`)
  2. Use two threads that both call `internalInitialize()` on the same component instance concurrently
  3. Wait for both threads to finish
  4. Assert that `onInitialize()` was called exactly 1 time
- Common pitfalls:
  - Testing only a single sequential call to `internalInitialize()` — this does not expose the race condition
  - Using `Thread.sleep()` with fixed durations to synchronize threads — use `CountDownLatch` or `CyclicBarrier` to reliably cause contention
  - Forgetting to wrap the count variable in an `AtomicInteger` or using `volatile` — the test itself must be thread-safe

  **Correct example (Java):**
  ```java
  @Test
  public void testConcurrentInitialization() throws Exception {
      AtomicInteger counter = new AtomicInteger(0);
      Component c = new Component("comp") {
          @Override
          protected void onInitialize() {
              counter.incrementAndGet();
          }
      };
      // Ensure both threads race to call internalInitialize
      int threadCount = 2;
      CountDownLatch latch = new CountDownLatch(threadCount);
      ExecutorService executor = Executors.newFixedThreadPool(threadCount);
      for (int i = 0; i < threadCount; i++) {
          executor.submit(() -> {
              latch.countDown();
              try { latch.await(); } catch (InterruptedException e) { Thread.currentThread().interrupt(); }
              c.internalInitialize();
          });
      }
      executor.shutdown();
      executor.awaitTermination(5, TimeUnit.SECONDS);
      assertEquals("onInitialize was called " + counter.get() + " times, expected 1", 1, counter.get());
  }
  ```

  **Incorrect example (sequential only, misses the race):**
  ```java
  @Test
  public void testInitialization() {
      Component c = new Component("comp") {
          @Override
          protected void onInitialize() {
              // do nothing
          }
      };
      c.internalInitialize();
      c.internalInitialize(); // second call in same thread — likely already protected by a flag
      // This does NOT test concurrent calls from different threads
  }
  ```