---
name: collection-modification-during-iteration
description: When calling toArray on a synchronized collection, the TG should test with concurrent modifications to ensure the iterator properly handles or fails fast. This skill is relevant for any collection wrapped with synchronizedList/synchronizedSet/synchronizedMap.
code_tags: ['EXCEPTION_HANDLING', 'VALIDATION', 'NULL_CHECK', 'BOUNDARY_CHECK']
test_pattern: EXCEPTION_TEST
---

# collection-modification-during-iteration

## Instructions

# Collection Modification During Iteration

## Instructions

- WHEN the TG encounters code that calls `toArray()` (or iterates over `toArray()`) on a collection that is wrapped with `Collections.synchronizedXXX()` — THEN the TG should write a test where a concurrent thread adds/removes elements from the synchronized collection while the main thread calls `toArray()`, and verify that either: (1) a `ConcurrentModificationException` is thrown (fail-fast behavior), OR (2) the operation completes without exception but the resulting array may be inconsistent (depending on the expected contract). The TG should verify the specific behavior expected by the code under test.

- WHEN the TG encounters a collection that is not explicitly designed for concurrent access (e.g., `ArrayList`, `HashSet`, `HashMap`) but is used from multiple threads — THEN the TG should write a test that exercises the collection under concurrent modification while calling `toArray()` and assert that either the method throws `ConcurrentModificationException` or that the test exposes the buggy behavior (e.g., incorrect array size, `ArrayStoreException`, or silent data corruption).

- Common pitfall: Testing `toArray()` only in single-threaded scenarios, which would never trigger `ConcurrentModificationException`. The TG must introduce concurrent modifications happening during the `toArray()` call, not before or after.

- Concrete values: Use `Collections.synchronizedList(new ArrayList<>())` or `Collections.synchronizedSet(new HashSet<>())`. Add elements from one thread while calling `toArray()` from another thread, with a `CountDownLatch` to ensure true concurrency.

### Example (Correct test approach):
```java
@Test
public void testToArrayWithConcurrentModification() {
    List<String> list = Collections.synchronizedList(new ArrayList<>());
    list.add("a");
    list.add("b");
    CountDownLatch latch = new CountDownLatch(1);
    ExecutorService executor = Executors.newSingleThreadExecutor();
    Future<?> future = executor.submit(() -> {
        latch.countDown();
        for (int i = 0; i < 1000; i++) {
            list.add("x");
        }
    });
    try {
        latch.await();
        // toArray() on a synchronizedList should not throw CME
        // but if the internal collection is incorrectly iterated, it might
        Object[] arr = ((AbstractList) list).toArray();
        // If bug is fail-fast breaking, may get ArrayStoreException or wrong size
        // Expected: no exception or specific exception depending on contract
    } catch (Exception e) {
        fail("Unexpected exception: " + e);
    }
    executor.shutdown();
}
```

### Example (Incorrect approach — missing concurrency):
```java
@Test
public void testToArrayWrong() {
    List<String> list = new ArrayList<>();
    list.add("a");
    list.add("b");
    Object[] arr = list.toArray();  // Single-threaded, never exercises bug
    assertEquals(3, arr.length);    // Fails differently than the actual bug
}
```