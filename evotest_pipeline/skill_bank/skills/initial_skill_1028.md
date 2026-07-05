---
name: cache-refresh-returns-stale-value-after-eviction
description: WHEN testing a cache with a refresh mechanism (e.g. CacheLIRS.refresh),
  THEN test that after an entry is evicted and then reloaded, calling refresh returns
  the newly loaded value, not the stale evicted value. This catches bugs where refresh
  uses an outdated internal reference instead of re-loading from the CacheLoader.
code_tags:
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# cache-refresh-returns-stale-value-after-eviction

## Instructions

# Testing Cache Refresh After Eviction

## Instructions

WHEN the TG encounters a cache implementation that supports a `refresh(K key)` method (such as `CacheLIRS.refresh(K)` which returns a `ListenableFuture<V>`), THEN the TG should write a test that:

1. Create a cache with a `CacheLoader` that tracks how many times it has been called (e.g., using an `AtomicInteger` counter).
2. Load a value for a key via `get(K)` or `getUnchecked(K)` — verify the loader is called exactly once.
3. Evict the entry by calling `invalidate(key)` to remove it from the cache.
4. Call `get(K)` again to reload the value — verify the loader is called a second time.
5. **Critical step**: Call `refresh(key)` on the cache and verify:
   - The `ListenableFuture` completes successfully (no `ExecutionException`).
   - The loader is called one additional time.
   - `get(key)` returns the value loaded by the most recent loader invocation (not the value loaded in step 4).

The TG must verify that the value returned after `refresh` is the value produced by the loader call triggered by `refresh`, not a stale value from the previous load. This requires comparing the actual returned value against a value that changes on each loader invocation (e.g., by appending a counter to the value).

Common pitfalls to avoid:
- **Testing refresh only on a pristine cache**: The bug surfaces specifically when refresh is called on a key whose entry was previously evicted and then reloaded. Test both the happy path (refresh on a resident entry) and the eviction-then-reload path.
- **Assuming refresh skips the loader**: Do not assume `refresh` returns immediately with the cached value. The contract of `refresh` is to asynchronously reload the value. Verify the future completes.
- **Not waiting for the future**: `refresh` returns a `ListenableFuture<V>`. The test must call `future.get()` to wait for completion before verifying the value.
- **Using `getIfPresent` after refresh**: After calling `refresh(key)`, use `get(key)` (which triggers loading) or wait on the returned future — do NOT use `getIfPresent` as it may return null before the async refresh completes.

### Correct Example (detects the bug):
```java
@Test
public void testRefreshAfterEviction() throws ExecutionException {
    AtomicInteger loaderCalls = new AtomicInteger();
    CacheLoader<Integer, String> loader = new CacheLoader<Integer, String>() {
        @Override
        public String load(Integer key) {
            return "value-" + loaderCalls.incrementAndGet();
        }
    };
    CacheLIRS<Integer, String> cache = new CacheLIRS<>(100);
    
    // Load entry - loader called once
    assertEquals("value-1", cache.get(1));
    
    // Evict the entry
    cache.invalidate(1);
    
    // Reload - loader called again (2nd call)
    assertEquals("value-2", cache.get(1));
    
    // Refresh - loader should be called again (3rd call)
    ListenableFuture<String> future = cache.refresh(1);
    assertEquals("value-3", future.get());  // Verifies refresh loaded the new value
    assertEquals("value-3", cache.get(1));  // Verifies cache now has refreshed value
}
```

### Incorrect Example (would miss the bug):
```java
// BUG: Never evicts the entry first; only tests refresh on a freshly loaded entry
CacheLIRS<Integer, String> cache = new CacheLIRS<>(100);
cache.get(1);  // loader call 1
cache.refresh(1).get();  // loader call 2
assertEquals("value-2", cache.get(1));
// This passes even with the buggy code because the bug only manifests
// when the entry was evicted and then reloaded before refresh.
```