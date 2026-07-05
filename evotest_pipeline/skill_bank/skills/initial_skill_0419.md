---
name: dispose-concurrent-merge-failure
description: WHEN testing dispose() lifecycle methods on resource-managed objects
  (like DocumentNodeStore), THEN verify that concurrent merge() operations fail gracefully
  with CommitFailedException instead of throwing unexpected exceptions or succeeding
  incorrectly. This skill covers testing shutdown-time concurrency safety where dispose()
  tears down resources while merges are in progress.
code_tags:
- RESOURCE_MANAGEMENT
- STATE_MUTATION
- CONCURRENCY
- DISPOSE_CONCURRENT_MERGE
test_pattern: INTERACTION_TEST
---

# dispose-concurrent-merge-failure

## Instructions

# Dispose Concurrent Merge Failure

## Instructions

WHEN the TG encounters a method named `dispose()` (or a similar shutdown/close lifecycle method) on a resource-managed object that supports concurrent `merge()` operations (e.g., `DocumentNodeStore`), THEN the TG should write a test that:

1. Calls `dispose()` on a separate thread while a concurrent `merge()` operation is in progress.
2. Uses synchronization primitives (e.g., `CountDownLatch`, `Semaphore`, `BlockingQueue`) to ensure that the `merge()` overlaps with the `dispose()` execution.
3. Expects the `merge()` call to throw a `CommitFailedException` — specifically by catching it and calling `fail("Merge must fail with CommitFailedException")` if the merge succeeds without an exception.
4. Tests that although the merge was concurrent with dispose, the system drains pending updates after dispose completes and that the store can still be safely read.

**Concrete types and values to use:**
- Use `DocumentNodeStore` as the class under test.
- Use `MemoryDocumentStore` as the backing store.
- Use `builderProvider.newBuilder().setAsyncDelay(0).setDocumentStore(...).setClusterId(...).getNodeStore()` to create the store.
- Use `store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY)` to perform merges.
- Use `store.dispose()` to trigger shutdown.
- Use `store.getRoot()` and `NodeBuilder` / `builder.child("childName")` to create test content.
- Use `CountDownLatch` or `BlockingQueue` with `offer()` and `poll(timeout, TimeUnit)` for synchronization between the dispose thread and the merge thread.
- Use `TimeUnit.SECONDS` for timeouts (e.g., `5` seconds in tests).

**What the test should verify:**
- That a `merge()` call concurrent with `dispose()` fails with a `CommitFailedException`.
- After the dispose completes, the store should still be able to drain updates (`store.runBackgroundOperations()`) without throwing exceptions.
- The test should not proceed past the failing merge unless the exception is caught.

**Common pitfalls to avoid:**
- ❌ **Not catching the exception**: The TG might let `merge()` throw an uncaught exception, failing the test unexpectedly. The test MUST catch `CommitFailedException` explicitly.
- ❌ **Calling `fail()` incorrectly**: The TG might write `fail()` unconditionally or forget to put it in the right place. It should be inside the catch block for a successful merge (i.e., `catch (CommitFailedException e) { /* expected */ }` with `fail("Merge must fail with CommitFailedException")` in the `try` block path).
- ❌ **Using Thread.sleep() for timing**: The TG might rely on `Thread.sleep()` to synchronize dispose with merge instead of using proper latches or queues. This leads to flaky tests.
- ❌ **Forgetting to run background operations after dispose**: The test should verify that `store.runBackgroundOperations()` can still be called after dispose to drain pending updates.
- ❌ **Reusing a disposed store for new merges**: After dispose, the test should NOT attempt new merges, only drain existing pending ones.

**Correct example pattern (Java):**

```java
final BlockingQueue<Object> queue = new ArrayBlockingQueue<Object>(1);
final DocumentNodeStore store = builderProvider.newBuilder()
    .setAsyncDelay(0)
    .setDocumentStore(new MemoryDocumentStore())
    .setClusterId(1)
    .getNodeStore();

// Thread 1: dispose
new Thread(new Runnable() {
    @Override
    public void run() {
        store.dispose();
        queue.offer("dispose done");
    }
}).start();

// Ensure dispose has started
NodeBuilder builder = store.getRoot().builder();
builder.child("child-1");
try {
    store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY);
    fail("Merge must fail with CommitFailedException");
} catch (CommitFailedException e) {
    // expected — dispose was concurrent with merge
}

// Drain pending updates after dispose
queue.poll(5, TimeUnit.SECONDS);
store.runBackgroundOperations();
```

**Incorrect pattern to avoid:**

```java
// WRONG: No synchronization, merge may succeed before dispose starts
DocumentNodeStore store = builderProvider.newBuilder()
    .setAsyncDelay(0)
    .setDocumentStore(new MemoryDocumentStore())
    .setClusterId(1)
    .getNodeStore();

new Thread(() -> { store.dispose(); }).start();
Thread.sleep(100); // flaky!

NodeBuilder builder = store.getRoot().builder();
builder.child("child-1");
store.merge(builder, EmptyHook.INSTANCE, CommitInfo.EMPTY); // might not fail
```