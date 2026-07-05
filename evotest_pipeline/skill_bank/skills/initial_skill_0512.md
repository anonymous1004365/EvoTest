---
name: caching-key-strict-mode-discrimination
description: When a cache uses a key containing a 'strict' boolean flag (like CacheKey),
  test that cache lookups with strict=true vs strict=false produce different results.
  Without this, a non-strict lookup result may be incorrectly reused for a strict
  lookup (or vice versa), causing false positive matches or missed matches.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- CACHE_NULL_RESULT
- CACHING_KEY_EQUALS_HASHCODE
test_pattern: INTERACTION_TEST
---

# caching-key-strict-mode-discrimination

## Instructions

# Cache Key Strict Mode Discrimination

## Instructions

- WHEN the code implements a caching layer (like `CachingResourceStreamLocator`) that delegates to another locator and caches results using a custom key class (like `CacheKey` extending `ResourceReference.Key`) that includes a `strict` boolean field in its `equals()`/`hashCode()` implementation
- THEN the TG MUST write an interaction-style test that:
  1. Uses a real delegate locator (like `ResourceStreamLocator` with `ClassPathResourceFinder`) — NOT a mock — to test actual resource lookup semantics
  2. For a resource that exists without locale variants (e.g., `org/apache/wicket/ajax/res/js/wicket-ajax-jquery-debug.js`), performs a **non-strict** lookup first with a specific locale (e.g., `new Locale("nl", "NL")`) — this should find the non-localized resource
  3. Then performs a **strict** lookup with the same locale — this should **NOT** find the resource (return `null`), because strict mode with a locale should not fall back to the non-localized version
  4. Asserts that the strict lookup returns `nullValue()`, proving the cache correctly distinguishes between strict and non-strict keys

- Common pitfall #1: Using mocks instead of a real delegate. Mocks bypass the actual resource resolution logic, so the test would not verify the real caching behavior against actual resource lookup semantics. Use `new ResourceStreamLocator(new ClassPathResourceFinder(""))` instead.

- Common pitfall #2: Only testing the "strict-then-non-strict" order. The bug can also manifest as "non-strict-then-strict" where the non-strict lookup caches a result, and the subsequent strict lookup incorrectly reuses that cached result. Test both orderings.

- Common pitfall #3: Using extension parameters like `".js"` or `null` that might change the test behavior. The fix and the bug both involve the `strict` flag in `CacheKey.equals()`/`hashCode()`, not the extension. Use `extension = null` and `style = null, variation = null` to keep the test focused on the strict/non-strict discrimination.

## Correct Example

```java
@Test
public void nonStrictMatchingDoesntResultInInvalidStrictMatch()
{
    IResourceStreamLocator resourceStreamLocator = new ResourceStreamLocator(
        new ClassPathResourceFinder(""));
    CachingResourceStreamLocator cachingLocator = new CachingResourceStreamLocator(
        resourceStreamLocator);

    String style = null;
    String variation = null;
    Locale locale = new Locale("nl", "NL");
    String extension = null;
    String filename = "org/apache/wicket/ajax/res/js/wicket-ajax-jquery-debug.js";

    // non-strict lookup should find the non-localized resource
    IResourceStream nonStrictLocate = cachingLocator.locate(
        AbstractDefaultAjaxBehavior.class, filename, style, variation, locale, extension, false);
    assertThat(nonStrictLocate, is(not(nullValue())));

    // strict lookup with a specific locale should NOT find the non-localized resource
    IResourceStream strictLocate = cachingLocator.locate(
        AbstractDefaultAjaxBehavior.class, filename, style, variation, locale, extension, true);
    assertThat(strictLocate, is(nullValue()));
}
```

## Incorrect Example

```java
// BAD: Using mock delegate - doesn't test actual resource resolution + caching interaction
@Test
public void badTest()
{
    IResourceStreamLocator delegate = mock(IResourceStreamLocator.class);
    when(delegate.locate(any(), anyString(), any(), any(), any(), any(), anyBoolean()))
        .thenReturn(new StringResourceStream("test"));
    
    CachingResourceStreamLocator cachingLocator = new CachingResourceStreamLocator(delegate);
    
    // Only tests that the cache returns the cached value, not that strict/non-strict differ
    IResourceStream result = cachingLocator.locate(
        String.class, "path", null, null, null, null, false);
    assertThat(result, is(not(nullValue())));
    
    // This would incorrectly pass because the mock always returns a value
    result = cachingLocator.locate(
        String.class, "path", null, null, null, null, true);
    assertThat(result, is(not(nullValue()))); // WRONG: should be nullValue() for strict with locale
}
```