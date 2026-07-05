---
name: concurrent-cache-load-race-npe
description: Use this skill when testing concurrent cache operations where multiple
  threads call `get(key)` with a `Callable<? extends V>` value loader. It guards against
  race conditions where internal state mutations (like segment resizing) can cause
  NPEs despite null-check guards.
code_tags:
- CONCURRENCY
- STATE_MUTATION
- NULL_CHECK
test_pattern: PARAMETRIC_TEST
---

# concurrent-cache-load-race-npe

## Instructions

# Concurrent Cache Load Race NPE Skill

## Instructions

- WHEN the TG encounters a cache class (like `CacheLIRS`) that:
  1. Has a `get(K key, Callable<? extends V> valueLoader)` method
  2. Internally performs segment array resizing or rehashing (e.g., arrays of segments that can be replaced)
  3. Has null-check guards like `if (segment == null) return null;` that appear to protect against null but are vulnerable to TOCTOU (time-of-check-to-time-of-use) races

- THEN the TG should write a test that exercises `get` with a callable value loader under **heavy concurrent segment resizing**. Specifically:
  - Create a small initial cache (e.g., 10 entries max, 2 segments) that triggers frequent resizing/expansion
  - Spawn multiple threads (at least 4-8) that continuously call `get(key, callable)` with different keys
  - Spawn at least one background thread that calls `put(key, value)` to trigger segment reallocation
  - The test must assert that **no NullPointerException is thrown** from any thread (wrap all operations in try-catch and collect failures)
  - Run the test for a sufficient duration (e.g., 5-10 seconds) to expose the race condition

- **Common Pitfalls:**
  - ❌ Testing only sequential single-threaded `get` operations — this will NOT expose the race
  - ❌ Testing only `getIfPresent()` or `getUnchecked()` — the bug is specific to `get(K, Callable<? extends V>)`
  - ❌ Using a large cache that never resizes — the race requires segment array replacement during concurrent loads
  - ❌ Not running the test long enough — the race window is tight; run for several seconds with many iterations
  - ❌ Asserting only that the final cache is correct — must assert that NO NPE occurred during the test

- **Correct Example:**
```java
// Correct: Heavy concurrent get() with callable, while a putter triggers resizing
CacheLIRS<Integer, String> cache = new CacheLIRS.Builder<Integer, String>()
    .maximumSize(10)
    .averageMemory(1)
    .segmentCount(2)
    .build();

AtomicInteger counter = new AtomicInteger();
AtomicReference<Throwable> failure = new AtomicReference<>();
List<Thread> threads = new ArrayList<>();

// Worker threads: continuously load
for (int i = 0; i < 8; i++) {
    Thread t = new Thread(() -> {
        for (int j = 0; j < 10000 && failure.get() == null; j++) {
            try {
                int key = counter.incrementAndGet() % 100;
                cache.get(key, () -> "value" + key);
            } catch (Throwable e) {
                failure.set(e);
            }
        }
    });
    threads.add(t);
}

// Put thread: triggers segment resizing
Thread putter = new Thread(() -> {
    for (int j = 0; j < 5000 && failure.get() == null; j++) {
        try {
            cache.put(j % 100, "newvalue" + j);
        } catch (Throwable e) {
            failure.set(e);
        }
    }
});
threads.add(putter);

threads.forEach(Thread::start);
threads.forEach(t -> t.join(10000));
assertNull("Got unexpected exception: " + failure.get(), failure.get());
```

- **Incorrect Example:**
```java
// ❌ Wrong: Only testing sequential, single-threaded get operations
CacheLIRS<Integer, String> cache = new CacheLIRS.Builder<Integer, String>()
    .maximumSize(100)
    .build();

// This will pass on buggy code and miss the NPE
String value = cache.get(42, () -> "hello");
assertEquals("hello", value);

// ❌ Wrong: Using getIfPresent instead of get(key, callable)
String v = cache.getIfPresent(42); // Won't trigger the buggy code path