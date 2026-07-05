---
name: lru-cache-eviction-service-lifecycle
description: When testing LRU caches that hold Service instances with eviction listeners,
  account for the asynchronous nature of Caffeine eviction notifications by explicitly
  calling cleanUp() and adding appropriate waits for async listener execution to complete
  before asserting state changes.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- CONCURRENCY
test_pattern: STATE_TEST
---

# lru-cache-eviction-service-lifecycle

## Instructions

# LRU Cache Eviction Service Lifecycle Verification

## Instructions

- WHEN the test involves an `LRUCache` (backed by Caffeine) that has `stopOnEviction=true` and stores `Service` instances (or extensions like `Producer`), and the test inserts more elements than `maximumCacheSize` to trigger evictions
- THEN after populating the cache beyond capacity and calling `cache.cleanUp()` to force eviction processing, the test MUST include a `Thread.sleep()` wait (e.g., 1000ms) before asserting that evicted services were stopped, because Caffeine's `onRemoval` listener with `RemovalCause.wasEvicted()` runs asynchronously by default (using a shared ForkJoinPool executor)
- The test should verify two things:
  1. The cache size is at `maximumCacheSize` (the LRU limit) after cleanup — e.g., `assertEquals("Size should be 5", 5, cache.size())`
  2. The number of evicted-and-stopped services equals (inserted - maxCacheSize) — e.g., `assertEquals(3, stopCounter.get())` for 8 inserted into a size-5 cache
- Common pitfalls:
  - Asserting the stop counter immediately after `cleanUp()` without sleeping, which will see 0 instead of the expected eviction count because the `onRemoval` callback has not yet executed
  - Forgetting that the eviction listener is invoked by Caffeine's executor (not the calling thread) unless `syncListener=true` was passed to the LRUCache constructor
  - Only testing cache size after eviction but not testing that the evicted services were properly stopped via the `onRemoval` → `ServiceHelper.stopService()` path
  - Using `Thread.sleep()` with insufficient duration — Caffeine's internal maintenance may schedule eviction listener execution with a delay; 1000ms is a safe default for test environments

### Correct example (from DefaultProducerCacheTest.testCacheStopExpired):
```java
public void testCacheStopExpired() throws Exception {
    ProducerCache cache = new ProducerCache(this, context, 5);
    cache.start();

    assertEquals("Size should be 0", 0, cache.size());

    for (int i = 0; i < 8; i++) {
        Endpoint e = new MyEndpoint(true, i);
        Producer p = cache.acquireProducer(e);
        cache.releaseProducer(e, p);
    }

    // the eviction is async so force cleanup
    cache.cleanUp();

    assertEquals("Size should be 5", 5, cache.size());

    // the eviction listener is async so sleep a bit
    Thread.sleep(1000);

    // should have stopped the 3 evicted
    assertEquals(3, stopCounter.get());

    cache.stop();

    // should have stopped all 8
    assertEquals(8, stopCounter.get());
}
```

### Incorrect example (what would fail on the buggy version):
```java
// BUGGY: no sleep after cleanUp() — eviction listener hasn't fired yet
public void testCacheStopExpired_Buggy() throws Exception {
    ProducerCache cache = new ProducerCache(this, context, 5);
    cache.start();
    for (int i = 0; i < 8; i++) {
        Endpoint e = new MyEndpoint(true, i);
        Producer p = cache.acquireProducer(e);
        cache.releaseProducer(e, p);
    }
    cache.cleanUp();
    assertEquals("Size should be 5", 5, cache.size());
    // FAILS: expected:<3> but was:<0>
    assertEquals(3, stopCounter.get());
    cache.stop();
}
```