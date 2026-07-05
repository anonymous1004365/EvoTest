---
name: async-callback-thread-context-preservation
description: When testing asynchronous callback methods on ProducerTemplate, verify
  that callbacks are invoked on the correct thread context (e.g., the original calling
  thread or a dedicated executor) and do not silently run on unexpected threads like
  a processor thread. This skill applies to any method accepting a callback that the
  framework invokes asynchronously.
code_tags:
- STATE_MUTATION
- VALIDATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# async-callback-thread-context-preservation

## Instructions

# Asynchronous Callback Thread Context Preservation

## Instructions

- **WHEN** the TG encounters a method like `asyncCallbackRequestBody`, `asyncCallbackSendBody`, or any `asyncCallback*` method on `DefaultProducerTemplate` (or similar `ProducerTemplate` implementations) that accepts a `Callback` argument,
- **THEN** the TG should write a test that verifies the *thread on which the callback is invoked*. In particular:
  - Use a custom processor in the route that observes/intercepts the exchange and records the current Thread name or identity.
  - In the callback, record the identity of the thread that invoked the callback (e.g., `Thread.currentThread().getName()`).
  - After both the processor and the callback have executed, assert that they ran on **different threads** (i.e., the callback thread is **not** the processor thread), OR assert that the callback ran on a specific expected thread (e.g., the main test thread or a dedicated executor thread), depending on the contract.
  - Use synchronization primitives like `CountDownLatch` and `AtomicReference<String>` to safely collect thread names across threads.
  - Expect an assertion failure on the buggy version where the callback incorrectly runs on the processor thread (same Thread), and pass on the fixed version where they run on different threads.

- **Common pitfalls to avoid**:
  - Testing only that the callback is *called* (not what thread it runs on). Thread identity is the key property.
  - Using `Thread.sleep()` for synchronization — use `CountDownLatch` instead.
  - Forgetting to share state (`AtomicReference`, `CountDownLatch`) across the processor and callback, which run on different threads.

- **Correct example (fixed version passes, buggy version fails)**:
```java
public void testAsyncCallbackThreadsInOutProcessor() throws Exception {
    final CountDownLatch latch = new CountDownLatch(2);
    final AtomicReference<String> processorThread = new AtomicReference<>();
    final AtomicReference<String> callbackThread = new AtomicReference<>();

    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:in").process(exchange -> {
                processorThread.set(Thread.currentThread().getName());
                latch.countDown();
            });
        }
    });
    context.start();

    template.asyncCallbackRequestBody("direct:in", "Hello", new Callback() {
        @Override
        public void done(boolean done) {
            callbackThread.set(Thread.currentThread().getName());
            latch.countDown();
        }
    });

    assertTrue("Both processor and callback should complete", latch.await(10, TimeUnit.SECONDS));
    assertNotNull("Processor should have run", processorThread.get());
    assertNotNull("Callback should have been invoked", callbackThread.get());
    assertNotEquals("Callback must NOT run on the processor thread",
        processorThread.get(), callbackThread.get());
}
```

- **Incorrect example (fails to detect the bug)**:
```java
public void testAsyncCallbackIsCalled() throws Exception {
    final CountDownLatch latch = new CountDownLatch(1);
    context.addRoutes(new RouteBuilder() {
        @Override
        public void configure() throws Exception {
            from("direct:in").process(exchange -> { });
        }
    });
    context.start();

    template.asyncCallbackRequestBody("direct:in", "Hello", new Callback() {
        @Override
        public void done(boolean done) {
            latch.countDown();
        }
    });

    assertTrue("Callback should be called", latch.await(10, TimeUnit.SECONDS));
    // BUG: does not check WHICH thread invoked the callback
}
```