---
name: cow-concurrent-index-copy
description: ''
code_tags:
- CONCURRENCY
test_pattern: INTERACTION_TEST
---

# cow-concurrent-index-copy

## Instructions

# Concurrent Copy-on-Write Index Directory Test

## Instructions

### WHEN
The TG encounters a Copy-on-Write (CoW) mechanism that lazily copies index files between directories (e.g., a root index directory and per-thread/context private copies), AND different threads may concurrently create/update different CoW copies while another thread reads metadata (like `fileExists()` or directory listings).

### THEN
Write a concurrent test that:
1. Creates multiple threads (e.g., at least 2 writer threads) that each use their **own separate** CoW index directory (e.g., different `IndexFolder` instances backed by different physical directories).
2. Has each writer thread perform an operation that triggers a CoW copy — for example, closing a writer on one index directory while another thread is actively reading the file listing of a **different** index directory.
3. Verifies that the operation on each thread completes without throwing an exception and that metadata (e.g., `fileExists()` checks for expected files) returns correct results for each directory independently.

### Common Pitfalls
- **Testing only a single index directory**: Do NOT test only one CoW directory in isolation. The bug manifests when multiple threads operate on *different* directories concurrently — one thread's write races with another thread's read of directory metadata.
- **Using sequential operations**: Do NOT run operations sequentially. The race condition requires overlapping concurrent execution.
- **Missing assertions for each directory**: After concurrent execution, verify expected state for each directory separately (e.g., `assertTrue("f1 should exist", d1.fileExists("f1"))`).
- **Ignoring concurrency primitives**: Use `CountDownLatch` or similar to ensure threads start at roughly the same time and overlap.

### Example (correct)

```java
@Test
public void cowConcurrentAccess() throws Exception {
    // two separate index directories backed by different dirs
    final IndexFolder f1 = copier.copy("/foo/bar");
    final IndexFolder f2 = copier.copy("/foo/bar2");

    final CountDownLatch latch = new CountDownLatch(1);
    final AtomicReference<Exception> ex1 = new AtomicReference<>();
    final AtomicReference<Exception> ex2 = new AtomicReference<>();

    Thread t1 = new Thread(() -> {
        try {
            latch.await();
            // operation that triggers CoW write on f1
            Directory d1 = f1.getIndexDir("a", "1");
            d1.close();
        } catch (Exception e) {
            ex1.set(e);
        }
    });

    Thread t2 = new Thread(() -> {
        try {
            latch.await();
            // operation that triggers CoW write on f2
            Directory d2 = f2.getIndexDir("b", "2");
            d2.close();
        } catch (Exception e) {
            ex2.set(e);
        }
    });

    t1.start();
    t2.start();
    latch.countDown();
    t1.join();
    t2.join();

    // verify no exceptions from either thread
    assertNull("Thread 1 exception: " + ex1.get(), ex1.get());
    assertNull("Thread 2 exception: " + ex2.get(), ex2.get());

    // verify each directory's existence independently
    assertTrue("f1 should exist", f1.fileExists("f1"));
    assertTrue("f2 should exist", f2.fileExists("f2"));
}
```

### Example (incorrect — will miss the bug)

```java
@Test
public void testSequentialCoW() throws Exception {
    // Only one directory, tested sequentially
    IndexFolder f = copier.copy("/foo/bar");
    Directory d1 = f.getIndexDir("a", "1");
    d1.close();
    assertTrue("f1 should exist", f.fileExists("f1"));
    // No concurrency — will not trigger the race
}
```