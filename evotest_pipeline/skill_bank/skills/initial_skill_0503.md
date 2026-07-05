---
name: caching-resource-locator-null-miss-behavior
description: When testing a caching resource locator that caches null results for
  missing resources, use a mock delegate to verify the cache-hit behavior — the delegate
  should only be called once even when locate() is invoked multiple times with the
  same key.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BUFFER_OFFSET_HANDLING
test_pattern: INTERACTION_TEST
---

# caching-resource-locator-null-miss-behavior

## Instructions

# Caching Resource Locator Null Result Caching

## Instructions

- WHEN the code under test is a caching wrapper (like `CachingResourceStreamLocator`) around a delegate resource locator (`IResourceStreamLocator`), and the caching locator stores `NullResourceStreamReference.INSTANCE` when the delegate returns `null`:
  - THEN verify the caching behavior by:
    1. Creating a mock `IResourceStreamLocator` delegate that returns `null` from `locate()`
    2. Passing the mock to the caching locator constructor
    3. Calling `locate()` twice (or more) with the exact same arguments (class + path)
    4. Verifying via Mockito `verify(delegate, times(1))` that the delegate was invoked only once
    5. Asserting that the second call returns `null` (since `NullResourceStreamReference.getReference()` returns `null`)

- WHEN the `locate(Class<?>, String)` 2-argument overload is used (not the full `locate(Class<?>, String, String, String, Locale, String, boolean)` overload):
  - THEN note that this overload internally creates a `CacheKey` with `strict=true` and all other fields (`extension`, `locale`, `style`, `variation`) set to `null`. Subsequent calls with the same `(Class, String)` arguments will hit the cache.

- Common pitfalls to avoid:
  - Do NOT test only the 'happy path' where the delegate returns a resource — you must also test that caching `null` results (missing resources) prevents repeated delegate calls.
  - Do NOT forget that the first call populates the cache and the second call should use the cached `NullResourceStreamReference` — verify the delegate call count is exactly 1, not 0 or 2.
  - Do NOT rely on a real `ResourceStreamLocator` for this test — use a mock so you have precise control over what the delegate returns.
  - Do NOT assume that calling `locate()` with different paths/key combinations tests the cache — each unique key is a separate cache entry.

### Example (correct)

```java
IResourceStreamLocator delegate = mock(IResourceStreamLocator.class);
when(delegate.locate(String.class, "path")).thenReturn(null);

CachingResourceStreamLocator cachingLocator = new CachingResourceStreamLocator(delegate);

// First call: delegate returns null, cached as NullResourceStreamReference
cachingLocator.locate(String.class, "path");
// Second call: should hit cache, delegate NOT called again
cachingLocator.locate(String.class, "path");

verify(delegate, times(1)).locate(String.class, "path");
```

### Example (incorrect — missing null caching test)

```java
IResourceStreamLocator delegate = mock(IResourceStreamLocator.class);
CachingResourceStreamLocator cachingLocator = new CachingResourceStreamLocator(delegate);

// Only tests two different calls — doesn't verify caching of null result
cachingLocator.locate(String.class, "path1");
cachingLocator.locate(String.class, "path2");
verify(delegate, times(2)).locate(any(), any()); // wrong — doesn't test cache hit
```