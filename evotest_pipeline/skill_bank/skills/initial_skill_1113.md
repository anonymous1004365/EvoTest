---
name: concurrent-commit-id-collision
description: When multiple threads concurrently commit to the same branch, the commit
  ID generation logic may produce duplicate IDs, causing a unique index or primary
  key violation when persisting. This skill teaches how to write a test that triggers
  concurrent commits and expects a primary key violation.
code_tags:
- CONCURRENCY
- PRIMARY_KEY_VIOLATION
- CONCURRENT_COMMIT_RACE
test_pattern: PARAMETRIC_TEST
---

# concurrent-commit-id-collision

## Instructions

# Concurrent Commit ID Collision

## Instructions

- WHEN the TG encounters a document store / revision-based commit system where commits to a branch retrieve a commit ID before persisting, AND multiple threads can perform this operation concurrently
- THEN the TG should write a test that:
  1. Uses CountDownLatch(2) to synchronize two threads so they both attempt to commit at nearly the same time
  2. Creates two threads that each perform a commit operation (e.g., `microKernel.commit(...)`) on the same branch
  3. Starts both threads, waits for both to finish, collects any exceptions
  4. Verifies that at least one thread either throws an exception wrapped around a `JdbcSQLException` with message containing "Unique index or primary key violation" OR the overall test checks that the persisted commit IDs are unique (no duplicate rows in the REVS table)
- Common pitfalls:
  - Test using only sequential (single-threaded) commits, which cannot expose the race condition
  - Using `Thread.sleep()` for synchronization instead of `CountDownLatch` — sleep is unreliable and may prevent the race from manifesting
  - Testing with `assertThrows` on a single thread call — the race requires two threads to interleave their commit-→ID-→persist sequence
  - Starting threads sequentially without ensuring they both reach the commit call before either  proceeds past it
  - Not using `ScheduledExecutorService` or `ExecutorService` with proper shutdown/awaitTermination

### Correct example (triggers the race reliably):

```java
@Test
public void testConcurrentCommitIdCollision() throws Exception {
    final int threadCount = 2;
    final CountDownLatch latch = new CountDownLatch(threadCount);
    final CountDownLatch startLatch = new CountDownLatch(1);
    ExecutorService executor = Executors.newFixedThreadPool(threadCount);
    List<Future<?>> futures = new ArrayList<>();
    for (int i = 0; i < threadCount; i++) {
        futures.add(executor.submit(() -> {
            try {
                startLatch.await();
                microKernel.commit("/", "+\"test\":{}", null, null);
            } catch (Exception e) {
                throw new RuntimeException(e);
            } finally {
                latch.countDown();
            }
        }));
    }
    startLatch.countDown();
    latch.await();
    executor.shutdown();
    int exceptionCount = 0;
    for (Future<?> f : futures) {
        try {
            f.get();
        } catch (ExecutionException e) {
            exceptionCount++;
            assertTrue(e.getCause().toString().contains("Unique index or primary key violation"));
        }
    }
    assertTrue("Expected at least one commit to fail with PK violation", exceptionCount >= 1);
}
```

### Incorrect example (sleep-based, unreliable):

```java
@Test
public void testConcurrentCommits_BAD() throws Exception {
    Thread t1 = new Thread(() -> mk.commit("/", "+\"x\":{}", null, null));
    Thread t2 = new Thread(() -> mk.commit("/", "+\"y\":{}", null, null));
    t1.start();
    Thread.sleep(100);
    t2.start();            
    t1.join();
    t2.join();
    // No assertion — may pass or fail randomly
}
```