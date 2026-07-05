---
name: concurrent-cache-random-operations
description: When testing a concurrent LIRS cache implementation (CacheLIRS), random
  operations tests with multiple threads exercising put/get/remove/cleanUp can expose
  race conditions and internal invariant violations. Use a PARAMETRIC test to stress
  the cache under concurrent random access patterns.
code_tags:
- CONCURRENCY
- CACHE_OPERATIONS
test_pattern: PARAMETRIC_TEST
---

# concurrent-cache-random-operations

## Instructions

# Concurrent Cache Random Operations Test

## Instructions

- WHEN the code under test is a concurrent LIRS cache (e.g., `CacheLIRS<K, V>`) with methods `put(K, V, int memory)`, `get(K)`, `getIfPresent(K)`, `remove(K)`, `cleanUp()`, `getMaxMemory()`, `getAverageMemory()`, `getUsedMemory()`, `containsValue(V)`, `stats()`, `entrySet()`, `keySet()`, and `peek(K)`
- THEN the TG should write a **PARAMETRIC_TEST** that:
  1. Creates a cache instance with a specific max memory (e.g., `100`) using `CacheLIRS.<K, V>newBuilder()`.
  2. Spawns **multiple concurrent threads** (e.g., `5` threads) that each execute a random sequence of operations for `N` iterations (e.g., `1000` or `10000` iterations per thread) in a tight loop — without sleeping between operations.
  3. In each iteration, the thread should randomly select an operation (e.g., via a `Random` instance) from a set that includes **at least**: `cache.put(key, value, memory)`, `cache.get(key)`, `cache.getIfPresent(key)`, `cache.remove(key)`, `cache.containsValue(value)`, `cache.getMaxMemory()`, `cache.getUsedMemory()`, `cache.getAverageMemory()`, `cache.peek(key)`, `cache.stats()`, `cache.keySet()`, `cache.entrySet()`.
  4. Ensure the test does **not** catch exceptions and swallow them — each operation should be allowed to throw (the test should use `assertThrows` for expected exceptions or let unexpected exceptions propagate and fail the test).
  5. After all threads complete, call `cache.cleanUp()` and verify internal consistency by inspecting `stats()`, `getUsedMemory()`, and ensuring no internal state corruption (no NPEs or illegal states).
  6. The test should use **thread-safe random number generation** (e.g., `ThreadLocalRandom.current()`) rather than a shared `Random` instance to avoid contention.

- Common pitfalls to avoid:
  - **Using `Thread.sleep()` or other coordination primitives** — the bug is a race condition that manifests only under heavy, unsynchronized concurrent access. Sleeping reduces or eliminates the interleaving that triggers the bug.
  - **Wrapping operations in try-catch and ignoring exceptions** — the test must not swallow exceptions like `NullPointerException`, `IllegalStateException`, or `ConcurrentModificationException`, as these are symptoms of the race condition.
  - **Using a single shared `Random` instance** — this creates artificial synchronization and reduces the likelihood of triggering the race. Use `ThreadLocalRandom` or per-thread `Random` instances.
  - **Testing only `put` and `get` operations** — the bug may involve `remove` + `cleanUp` + `getIfPresent` interleavings. Include a broad set of cache operations in the random mix.
  - **Using a cache with a very large max memory** — a small max memory (e.g., `100`) triggers eviction more frequently, increasing the chance of hitting the race condition.

### Correct Example (excerpt from ConcurrentTest.testRandomOperations)

```java
@Test
public void testRandomOperations() throws Exception {
    Random rnd = new Random();
    int threads = 5;
    int operations = 10000;
    CacheLIRS<Integer, Integer> cache = CacheLIRS.<Integer, Integer>newBuilder()
            .maximumWeight(100).averageWeight(1).build();
    List<Thread> list = new ArrayList<>();
    for (int i = 0; i < threads; i++) {
        Thread t = new Thread(() -> {
            Random r = ThreadLocalRandom.current();
            for (int j = 0; j < operations; j++) {
                int key = r.nextInt(200);
                int op = r.nextInt(100);
                if (op < 40) {
                    cache.put(key, key, 1);
                } else if (op < 60) {
                    cache.get(key);
                } else if (op < 80) {
                    cache.getIfPresent(key);
                } else if (op < 90) {
                    cache.remove(key);
                } else if (op < 95) {
                    cache.containsValue(key);
                } else {
                    cache.getMaxMemory();
                    cache.getUsedMemory();
                }
            }
        });
        t.start();
        list.add(t);
    }
    for (Thread t : list) {
        t.join();
    }
    cache.cleanUp();
    // Verify no corruption: stats() etc. should not throw
    assertNotNull(cache.stats());
}
```

### Incorrect Example (swallows exceptions, sleeps between operations)

```java
@Test
public void testRandomOperationsFlawed() throws Exception {
    Random rnd = new Random(42);
    CacheLIRS<Integer, Integer> cache = ...;
    Thread t = new Thread(() -> {
        for (int j = 0; j < 100; j++) {
            try {
                cache.put(rnd.nextInt(200), rnd.nextInt(200), 1);
                Thread.sleep(1);  // BAD: reduces interleaving
            } catch (Exception e) {
                // BAD: swallows clues about the race condition
            }
        }
    });
    t.start();
    t.join();
}
```