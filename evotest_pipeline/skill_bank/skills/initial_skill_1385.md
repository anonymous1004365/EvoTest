---
name: flush-deadlock-detection
description: When a WriteOperationHandler has a flush method that waits for in-flight
  write operations to complete before flushing, a deadlock can occur if a write operation's
  callback itself triggers another flush. This skill teaches how to test for such
  flush-induced deadlocks using multi-threaded test scenarios.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: INTERACTION_TEST
---

# flush-deadlock-detection

## Instructions

# Detecting Flush Deadlocks via Nested Flush Invocation

## Instructions

- **WHEN** the TG encounters a `WriteOperationHandler` (or similar resource pool manager) whose `flush()` method waits for borrowed/in-flight writers to be returned before proceeding, and where `flush()` is designed to block until borrowed resources are released,
- **THEN** the TG should write a test that reproduces a circular blocking scenario: from within a `WriteOperation.execute()` callback running on one thread, submit a `Callable` to a *different* executor thread that calls `flush()` on the same pool, and verify that `flush()` times out (proving a deadlock was avoided or detected).

- **Concretely**:
  1. Create a `WriteOperation` whose `execute()` method:
     - Submits a `Callable<Void>` to a second executor (e.g., `executors[1]`), where that callable calls `pool.flush(store)`.
     - Captures the `Future` from that submission and calls `future.get(timeout, MILLISECONDS)`.
     - If `TimeoutException` is thrown (the flush deadlocks as expected), return a valid `RecordId` to indicate the deadlock was caught.
     - If no exception or other exception is thrown (flush completed), return `null` to indicate test failure (no deadlock protection).
  2. Execute this `WriteOperation` via the pool on a first executor thread.
  3. Assert that the `Future` returns the valid `RecordId`, proving the deadlock was detected.

- **Common pitfalls**:
  - ❌ Testing flush and write operations sequentially (single-threaded) — this will NOT catch the deadlock since true concurrency is required.
  - ❌ Using the same executor for both the write operation and the flush call — the deadlock requires two different threads: one holding the borrowed writer and another calling flush.
  - ❌ Not using a timeout on `future.get()` — without a timeout the test will hang indefinitely on the buggy version if the deadlock never resolves.
  - ❌ Returning `null` or throwing from the write operation instead of using a recognizable sentinel value like `rootId` to distinguish "deadlock detected" from "other failure".
  - ❌ Forgetting that `@CheckForNull` may need to be added on the return annotation of the overridden `execute()` method, since the test returns `null` in the failure case.

- **Example correct implementation**:
```java
@Test
public void testFlushBlocks() throws ExecutionException, InterruptedException {
    Future<RecordId> res = execute(new WriteOperation() {
        @Nonnull
        @CheckForNull @Override
        public RecordId execute(@Nonnull SegmentBufferWriter writer) {
            try {
                executors[1].submit(new Callable<Void>() {
                    @Override
                    public Void call() throws Exception {
                        pool.flush(store);
                        return null;
                    }
                }).get(100, MILLISECONDS);
                return null;    // No deadlock -> failure
            } catch (InterruptedException | ExecutionException ignore) {
                return null;    // No deadlock -> failure
            } catch (TimeoutException ignore) {
                return rootId;  // Deadlock -> expected behavior
            }
        }
    }, 0);
    assertEquals(rootId, res.get());
}
```

- **Example incorrect implementation** (will NOT catch the bug):
```java
@Test
public void testFlushBlocks_Wrong() throws Exception {
    // Single-threaded, no concurrency — does not reproduce the deadlock
    pool.flush(store);  // This just works on its own
    // No assertion about deadlock behavior at all
}
```