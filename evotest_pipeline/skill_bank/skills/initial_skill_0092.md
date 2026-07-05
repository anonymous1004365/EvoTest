---
name: early-cancel-flag-initialization
description: When a class has cancel/stop lifecycle methods that can be called before
  the main execution starts, the cancel state flags must be properly initialized so
  that early cancel() calls take effect. This skill helps write tests that verify
  cancel-before-invoke behavior.
code_tags:
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# early-cancel-flag-initialization

## Instructions

# Early Cancel Flag Initialization

## Instructions

WHEN the TG encounters a class that has a `cancel()` or `stop()` method that sets a boolean flag (e.g., `canceled`, `isRunning`) AND the main execution flow (`run()`, `invoke()`) checks this flag to determine whether to proceed or terminate early, THEN the TG should write a test that calls `cancel()` **before** the execution method (`invoke()`, `run()`) starts, and verify that the task/thread/execution is properly canceled.

Specifically:
- The boolean flag must be initialized to `true` (for `isRunning`-style flags) or default appropriately (e.g., `canceled` initialized to `false` before `cancel()` sets it to `true`), so that an early cancel before invoke takes effect.
- Initialize the test object (e.g., `StreamTask`) with mocks that block or latch in the `invoke()` method so the test can control timing.
- Call `cancel()` on the object **before** starting `invoke()`.
- Then start `invoke()` in a separate thread.
- Verify that the task completes cancelation (e.g., the thread finishes, `canceled` flag is `true`, the `run()` method terminated early).
- Use a timeout mechanism (e.g., `OneShotLatch`, `CountDownLatch`, `FiniteDuration` deadline) to avoid infinite waiting.

**Common pitfalls to avoid:**
- **Do NOT** start the task execution first and then cancel — that tests normal cancel, not early cancel. The whole point is cancel-before-execution-starts.
- **Do NOT** forget to use a separate thread — `invoke()` may block, so calling it directly would deadlock the test.
- **Do NOT** test cancel flags in isolation without actually running the lifecycle — the bug is that the flag transition doesn't happen because initialization order is wrong.
- **Do NOT** assume that setting a `canceled` flag is enough — verify that the task actually terminates (thread joins, latch released, etc.)
- **Do NOT** rely solely on mock verification that `cancel()` was called — the test must verify the **observable consequence** (task stopped, flag changed, execution exited early).

**Example (correct — tests early cancel with a blocking source):**

```java
@Test
public void testEarlyCanceling() throws Exception {
    StreamConfig cfg = new StreamConfig(new Configuration());
    cfg.setOperatorID(new OperatorID(4711L, 42L));
    cfg.setStreamOperator(new StreamSource<>(new BlockingSource()));

    // Use mock environment / task that provides necessary services
    try (StreamTask<?, ?> task = createTask(cfg)) {
        // Cancel BEFORE invoke
        task.cancel();
        
        // Start invoke in a separate thread
        Thread invokeThread = new Thread(() -> {
            try {
                task.invoke();
            } catch (Exception e) {
                // expected
            }
        });
        invokeThread.start();
        
        // Wait for invoke to finish (task did cancel)
        invokeThread.join(5000); // timeout after 5s
        
        // Verify the thread terminated (i.e., cancel took effect)
        assertFalse("Task did not cancel", invokeThread.isAlive());
        assertTrue("Task did not become canceled", task.isCanceled());
    }
}
```

**Example (incorrect — starts task then cancels, which tests normal cancel, not early cancel):**

```java
// WRONG: This tests cancellation DURING execution, not BEFORE
@Test
public void testCancelingDuringExecution() throws Exception {
    try (StreamTask<?, ?> task = createTask(cfg)) {
        Thread invokeThread = new Thread(() -> task.invoke());
        invokeThread.start();
        
        // Wait for task to start running, then cancel
        Thread.sleep(100);
        task.cancel();  // This tests mid-execution cancel, not early cancel
        
        invokeThread.join(5000);
        assertFalse(invokeThread.isAlive());
    }
}
```

**Example (incorrect — no separate thread, will deadlock):**

```java
// WRONG: invoke() blocks synchronously, this will hang forever on buggy code
@Test
public void testEarlyCancelingWrong() throws Exception {
    try (StreamTask<?, ?> task = createTask(cfg)) {
        task.cancel();
        task.invoke();  // This blocks! Test never finishes.
    }
}
```