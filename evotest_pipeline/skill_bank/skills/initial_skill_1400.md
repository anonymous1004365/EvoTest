---
name: concurrent-revision-uniqueness
description: When generating tests for a `newRevision(int clusterId)` method that
  uses lazy timestamp read combined with synchronized counter logic, test that multiple
  threads never produce duplicate revisions. This skill applies to any revision/timestamp
  utility where uniqueness depends on both a method-local timestamp and a class-level
  synchronized counter.
code_tags:
- CONCURRENCY
- CONCURRENT_COUNTER_RACE
test_pattern: PARAMETRIC_TEST
---

# concurrent-revision-uniqueness

## Instructions

# Concurrent Revision Uniqueness

## Instructions

- WHEN the TG encounters a `static Revision newRevision(int clusterId)` method that:
  1. Calls `getCurrentTimestamp()` (or similar) **outside** the `synchronized` block to obtain a timestamp
  2. Then enters a `synchronized (ClassName.class)` block where it compares the method-local timestamp against a `static volatile long lastRevisionTimestamp`
  3. Increments a `static volatile int lastRevisionCount` counter when timestamps match, or resets both when a newer timestamp is detected
- THEN the TG must write a high-concurrency test that:
  - Creates **at least 20 threads** (matching the concurrency level that exposed the bug)
  - Each thread repeatedly calls `Revision.newRevision(clusterId)` (e.g., `clusterId = 1`) in a tight loop (e.g., 1024 iterations per batch)
  - Collects all generated `Revision` objects into a shared **synchronized** `Set<Revision>` (e.g., `Collections.synchronizedSet(new HashSet<>())`)
  - Continuously checks that each new revision can be added to the set, and if `set.add(r)` returns `false`, records it as a duplicate
  - Lets threads run for a fixed duration (e.g., 200ms) via `Thread.sleep(200)` then signals them to stop with an `AtomicBoolean`, and joins all threads
  - **Asserts** that `duplicate[0]` (or equivalent holder) is `null` — i.e., no duplicate revision was ever produced
  - The test must **fail** on the buggy code with a message like "Duplicate revision" (not `null`)
- Include the following **common pitfalls** to avoid:
  - ❌ **Pitfall: Testing with only 1 or 2 threads** — The race condition manifests only under high contention (10+ threads). Low thread counts may never trigger the timing window.
  - ❌ **Pitfall: Running too few iterations per thread** — The bug involves a window between the timestamp read and the synchronized counter check. Tight loops (hundreds or thousands of iterations) are needed to hit the race.
  - ❌ **Pitfall: Using a non-synchronized Set** — `HashSet` is not thread-safe; concurrent `add` operations from multiple threads can cause data corruption. Always use `Collections.synchronizedSet(new HashSet<>())`.
  - ❌ **Pitfall: Failing to join threads before asserting** — Without `t.join()`, the main thread may check for duplicates while worker threads are still running, leading to flaky results.
  - ❌ **Pitfall: Using the same `clusterId` for multiple test runs that interfere** — The static fields `lastRevisionTimestamp` and `lastRevisionCount` are shared across tests. Reset clock state between tests with `Revision.resetClockToDefault()` if needed, or use a distinct `clusterId` per test to avoid cross-test pollution.

### Correct example (conceptual structure):
```java
// In a test class for Revision
@Test
public void uniqueRevision2() throws Exception {
    List<Thread> threads = new ArrayList<>();
    AtomicBoolean stop = new AtomicBoolean();
    Set<Revision> set = Collections.synchronizedSet(new HashSet<>());
    Revision[] duplicate = new Revision[1];

    for (int i = 0; i < 20; i++) {
        Thread t = new Thread(() -> {
            Revision[] last = new Revision[1024];
            while (!stop.get()) {
                for (Revision r : last) { set.remove(r); }
                for (int i = 0; i < last.length; i++) {
                    last[i] = Revision.newRevision(1);
                }
                for (Revision r : last) {
                    if (!set.add(r)) { duplicate[0] = r; }
                }
            }
        });
        t.start();
        threads.add(t);
    }
    Thread.sleep(200);
    stop.set(true);
    for (Thread t : threads) { t.join(); }
    assertNull("Duplicate revision", duplicate[0]);
}
```

### Incorrect example (won't catch the bug):
```java
// ❌ Too few threads, too few iterations
@Test
public void weakUniquenessTest() {
    Set<Revision> set = new HashSet<>();
    for (int i = 0; i < 100; i++) {
        set.add(Revision.newRevision(1));
    }
    // Single-threaded: never exercises the race condition
    assertEquals(100, set.size());
}
```