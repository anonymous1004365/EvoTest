---
name: compaction-gc-state-mutation-under-concurrent-reads
description: Detects state mutation bugs in compaction/garbage-collection cycles where
  shared state (e.g. segment maps, reference counters) is mutated without synchronization
  while concurrent reads access the same data. When the TG sees compaction or GC logic
  that clears, resets, or rebuilds shared collections, it should test with concurrent
  read operations to trigger race conditions.
code_tags:
- STATE_MUTATION
- OVERFLOW
test_pattern: STATE_TEST
---

# compaction-gc-state-mutation-under-concurrent-reads

## Instructions

# Compaction Garbage Collection State Mutation Under Concurrent Reads

## Instructions

WHEN the TG encounters a compaction or garbage-collection implementation that mutates shared state during a compaction cycle (e.g., clearing a segment map, resetting reference counters, rebuilding a segment store's internal data structures like `segmentMap`, `segmentCache`, or `refCounts`), and those data structures are also read by concurrent accessor methods (e.g., `containsSegment()`, `readSegment()`, `getSegmentId()`):

- THEN the TG should write a test that:
  1. Sets up a segment store with at least one existing segment entry in the shared state.
  2. Starts a compaction/GC operation in a background thread that mutates the shared state (e.g., calls `compact()` or `gc()` on the store).
  3. While the compaction is in progress, from the main thread, performs concurrent read operations on the **same store instance** (e.g., repeatedly calls `store.containsSegment(segmentId)`).
  4. Verifies that both the compaction completes without throwing an exception AND the concurrent reads do not encounter `NullPointerException`, `ConcurrentModificationException`, `ArrayIndexOutOfBoundsException`, or produce `false` negatives (e.g., `containsSegment` incorrectly returning `false` for segments that exist and were not removed).

- **Common pitfalls to avoid:**
  - Testing only sequential compaction without concurrent readers — the bug manifests only under concurrent access.
  - Using separate store instances for reads and writes — the collision must happen on the **same** store object.
  - Assuming compaction is idempotent or that reads after compaction will pass — the bug is that reads **during** compaction fail.
  - Not verifying that the compaction actually mutates shared state — read the implementation to confirm that `clear()`, `reset()`, or `put()` is called on shared collections during compaction.
  - Using `ConcurrentHashMap` or other concurrent collections as a panacea — the bug can also be caused by logic that temporarily removes entries and re-adds them in non-atomic order.

- **Concrete example (correct test pattern):**

```java
// Correct: Tests that concurrent reads during compaction don't NPE
@Test
public void testConcurrentReadsDuringCompaction() throws Exception {
    SegmentStore store = new FileStore(...);
    // Pre-populate with segments that will be read concurrently
    SegmentId segmentId = store.getSegmentId(...);
    store.writeSegment(segmentId, ...);
    
    // Start compaction on a background thread
    ExecutorService executor = Executors.newSingleThreadExecutor();
    Future<?> compactionFuture = executor.submit(() -> {
        store.compact();  // or store.gc()
    });
    
    // Concurrently read the same store
    for (int i = 0; i < 100; i++) {
        assertNotNull("Segment should still be accessible during compaction",
            store.containsSegment(segmentId));
    }
    
    compactionFuture.get(30, TimeUnit.SECONDS);
    executor.shutdown();
}
```

- **Incorrect test pattern to avoid:**

```java
// INCORRECT: Sequential-only, no concurrency, misses the bug entirely
@Test
public void testCompactionSequentially() throws Exception {
    SegmentStore store = new FileStore(...);
    store.writeSegment(...);
    store.compact();  // compaction completes without concurrent reads
    // This passes even when concurrent reads would fail during compaction
    assertTrue(store.containsSegment(segmentId));
}
```