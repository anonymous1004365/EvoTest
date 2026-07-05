---
name: destroy-all-buffer-pools-resource-leak
description: When a resource-managing class (like NetworkBufferPool) has a destroyAll
  method that clears internal collections, test that resources allocated before the
  destroy are properly cleaned up and not leaked. Use this skill when testing batch
  cleanup of pooled resources.
code_tags:
- STATE_MUTATION
- RESOURCE_MANAGEMENT
test_pattern: STATE_TEST
---

# destroy-all-buffer-pools-resource-leak

## Instructions

# DestroyAll-BufferPools Resource Leak Detection

## Instructions

**WHEN** the TG encounters a class that manages pooled resources (e.g., `BufferPool` instances registered in a `NetworkBufferPool`) and exposes a `destroyAll` (or similar batch-cleanup) method that clears internal collections:

- **THEN** the TG should write a test that:
  1. Allocates one or more resources (`requestBufferPool(...)`) via the manager
  2. Calls the batch cleanup method (e.g., `destroyAllBufferPools()`)
  3. Verifies that the manager's internal resource accounting (e.g., `getNumberOfRegisteredBufferPools()`) returns **zero** after the cleanup
  4. Verifies that the manager can still allocate new resources after the cleanup (no leaked references or corrupted state)

**Concrete example from the bug:**
- Class: `NetworkBufferPool` (in `flink-runtime`)
- Method: `destroyAllBufferPools()` — iterates over `allBufferPools` and destroys each one, but **the buggy version did not clear the collection afterwards**, causing resource leaks and `IllegalStateException` on subsequent operations
- Test class: `NetworkBufferPoolTest`
- Test method: `testDestroyAll` — allocates a buffer pool, calls `destroyAllBufferPools()`, verifies `getNumberOfRegisteredBufferPools() == 0`

**Common pitfalls to avoid:**
- ❌ Testing only that `destroyAll` runs without exception — the collection may still hold references
- ❌ Forgetting to verify the internal counter (`getNumberOfRegisteredBufferPools()`) after the destroy
- ❌ Forgetting to test that the manager is reusable after `destroyAll` (no leaked state that blocks new allocations)
- ✅ Always check both: the collection size AND that new allocations succeed afterward

**Correct test pattern (Java/JUnit):**
```java
@Test
public void testDestroyAll() {
    NetworkBufferPool globalPool = new NetworkBufferPool(256, 1024);
    // Allocate a buffer pool
    globalPool.createBufferPool(1, 1);
    // Destroy all
    globalPool.destroyAllBufferPools();
    // Verify no registered pools remain
    assertEquals(0, globalPool.getNumberOfRegisteredBufferPools());
}
```

**Incorrect test pattern:**
```java
@Test
public void testDestroyAll() {
    NetworkBufferPool globalPool = new NetworkBufferPool(256, 1024);
    globalPool.createBufferPool(1, 1);
    // Missing: no check of registered pool count
    globalPool.destroyAllBufferPools(); // passes even if collection not cleared
    // New allocations may fail with IllegalStateException
}
```