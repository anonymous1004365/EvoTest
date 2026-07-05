---
name: long-multi-principal-entry-overflow-check
description: When summing permission entry counts across multiple principals, guard
  against overflow where safeAdd may return Long.MAX_VALUE for one principal, which
  then gets capped by the overflow check incorrectly — the cumulative total may overflow
  and exceed the max cache size threshold, causing premature cache eviction or preloading.
  Use this skill when testing arithmetic on large long values summed across iterations.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- ARITHMETIC_OVERFLOW
- CACHE_OPERATIONS
test_pattern: STATE_TEST
---

# long-multi-principal-entry-overflow-check

## Instructions

# Long Multi-Principal Entry Count Overflow Guard

## Instructions

WHEN the TG encounters a `PermissionEntryProviderImpl.init()` method (or similar method) that:
- Iterates over a collection of principal names
- Calls `cache.getNumEntries(store, name, maxSize)` (or equivalent) for each principal, which may return `Long.MAX_VALUE`
- Accumulates the result using `LongUtils.safeAdd(cnt, n)` into a running total `cnt`
- Has a guard like `if (cnt < Long.MAX_VALUE)` before calling `safeAdd` to avoid overflow
- Then uses the accumulated count to decide whether to preload the cache (e.g., `if (cnt > 0 && cnt < maxSize)`)

THEN the TG should:

1. **Test with multiple principals where at least one returns a very large count near Long.MAX_VALUE**. Specifically:
   - Use a principal that returns `Long.MAX_VALUE` for `getNumEntries` (indicating "unknown, too many to count")
   - Use a second principal that returns a small positive count (e.g., 50)
   - Verify that the cumulative `cnt` equals `Long.MAX_VALUE` (clamped by the overflow guard), and that the cache preloading decision (the `if (cnt > 0 && cnt < maxSize)` check) evaluates to `false`, so `pathEntryMap` is `null`
   - Verify that `existingNames` still contains all principals that had `n > 0` entries

2. **Test with three principals**: one returning `Long.MAX_VALUE - 10`, one returning `50`, and one returning `0` (no entries):
   - Verify `existingNames` does NOT include the principal that returned 0
   - Verify `cnt` does NOT overflow into a negative value or incorrectly wrap around below `maxSize`
   - Verify the cache is NOT preloaded (the pathEntryMap should be null) because the cumulative count exceeds maxSize

3. **Test the edge case where safeAdd returns Long.MAX_VALUE due to overflow**:
   - The safeAdd overflow check in the accumulation logic must ensure that once `cnt` is set to `Long.MAX_VALUE` (because one principal returned `Long.MAX_VALUE`), subsequent additions don't overflow further or cause incorrect state
   - Verify that `pathEntryMap` is `null` when `cnt >= maxSize`

4. **Use reflection** to access private fields (like `existingNames`, `pathEntryMap`) to verify internal state after initialization.

5. **Mock the store and cache** to control what `getNumEntries` returns per principal, and make the cache's `load()` method fail with a `fail("The number of entries exceeds the max cache size")` assertion so that any attempt to preload entries beyond the limit is caught.

**Common pitfalls to avoid:**
- Testing only a single principal with `Long.MAX_VALUE` — the bug manifests specifically when summing across MULTIPLE principals where the sum would overflow
- Forgetting to verify `existingNames` is properly populated even when the total `cnt` indicates too many entries to cache
- Assuming safeAdd is sufficient without the surrounding `if (cnt < Long.MAX_VALUE)` guard — the guard prevents calling safeAdd when cnt is already saturated at MAX_VALUE
- Using `n == Long.MAX_VALUE` to detect overflow without checking whether `cnt` itself might have already been set to `Long.MAX_VALUE` by a previous iteration

**Correct example (inspired by the triggering test):**
```java
@Test
public void testInitLongOverflow2() throws Exception {
    MockPermissionStore store = new MockPermissionStore();
    PermissionEntryCache cache = new MockPermissionEntryCache();
    Set<String> principalNames = ImmutableSet.of(GROUP_LONG_MAX_MINUS_10, GROUP_50);
    // GROUP_LONG_MAX_MINUS_10.getNumEntries returns Long.MAX_VALUE - 10
    // GROUP_50.getNumEntries returns 50
    // safeAdd(Long.MAX_VALUE - 10, 50) returns Long.MAX_VALUE (overflow clamp)
    // The guard checks: if (cnt < Long.MAX_VALUE) { cnt = safeAdd(cnt, n); }
    // But cnt starts at 0, after first principal: cnt = Long.MAX_VALUE - 10
    // After second principal: cnt = Long.MAX_VALUE (safeAdd returns MAX_VALUE due to overflow)
    // Since cnt (Long.MAX_VALUE) > maxSize (250), pathEntryMap remains null
    PermissionEntryProviderImpl provider = new PermissionEntryProviderImpl(store, cache, principalNames, ConfigurationParameters.EMPTY);
    Set<String> existingNames = getExistingNames(provider);
    assertEquals(principalNames, existingNames);
    assertNotSame(Iterators.emptyIterator(), provider.getEntryIterator(new EntryPredicate()));
}
```

**Incorrect example:**
```java
// BAD: Only testing with one principal returning Long.MAX_VALUE
// This doesn't catch the multi-principal cumulative overflow bug
@Test
public void testSinglePrincipalOverflow() {
    // Only one principal with Long.MAX_VALUE — no sum overflow to test
    MockPermissionStore store = new MockPermissionStore();
    PermissionEntryCache cache = new MockPermissionEntryCache();
    Set<String> principalNames = ImmutableSet.of("groupLongMax");
    PermissionEntryProviderImpl provider = new PermissionEntryProviderImpl(store, cache, principalNames, ConfigurationParameters.EMPTY);
    // This doesn't exercise the safeAdd accumulation across multiple iterations
}
```