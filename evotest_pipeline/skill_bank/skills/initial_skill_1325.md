---
name: resource-caching-version-mismatch
description: WHEN the TG encounters resource caching strategies (like QueryStringWithVersionResourceCachingStrategy
  or FilenameWithVersionResourceCachingStrategy) that conditionally set cache duration
  to maximum when versions match, THEN it should test the lifecycle where a URL without
  a version parameter is undecorated (storing null/empty version metadata) before
  decorateResponse is called, ensuring the version mismatch path is exercised. Common
  pitfalls include testing only the version-match happy path or failing to simulate
  the full undecorate-before-decorate request lifecycle.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: STATE_TEST
---

# resource-caching-version-mismatch

## Instructions

# Resource Caching Version Mismatch Handling

## Instructions

**WHEN** the TG encounters a resource caching strategy (implementing `IResourceCachingStrategy`) that conditionally enables maximum caching based on version matching — specifically a `decorateResponse(response, resource)` method that compares `requestedVersion` (stored as metadata `IResourceCachingStrategy.URL_VERSION` in the `RequestCycle`) with `calculatedVersion` (from `resourceVersion.getVersion(resource)`) and calls `response.setCacheDurationToMaximum()` / `response.setCacheScope(WebResponse.CacheScope.PUBLIC)` only when they match:

- **THEN** the TG must test that when the versions do NOT match, the response cache duration defaults to the application's `ResourceSettings.getDefaultCacheDuration()` (e.g., `Duration.minutes(60)`) and the cache scope defaults to `WebResponse.CacheScope.PRIVATE`.
- **THEN** the TG must simulate the full request lifecycle: first call `strategy.undecorateUrl(url)` with a URL that has NO version parameter (or a mismatched version) so that the `requestCycle.setMetaData(URL_VERSION, ...)` stores either `null` or a mismatched value, then call `strategy.decorateResponse(response, resource)` and verify the resulting cache settings.
- **THEN** the TG must verify that when `requestedVersion` is `null` (no version found in URL), the response uses the default cache duration and `PRIVATE` scope, NOT the maximum cache duration.
- **THEN** the TG must verify that `ResourceResponse.getCacheDuration()` returns the expected `Duration` object — for the version-mismatch case, it should equal the configured `defaultCacheDuration` (e.g., `Duration.minutes(60)`), and for the version-match case it should equal `WebResponse.MAX_CACHE_DURATION` (which is `Duration.days(365)`).
- **THEN** the TG must verify that `ResourceResponse.getCacheScope()` returns `WebResponse.CacheScope.PRIVATE` for version mismatch and `WebResponse.CacheScope.PUBLIC` for version match.

**Common pitfalls:**
- Testing only the version-match path and assuming the default values are correct without verification
- Not setting up a `RequestCycle` via a tester (e.g., `BaseWicketTester`) before calling `decorateResponse`, which requires `RequestCycle.get()` to return a non-null value
- Forgetting to call `undecorateUrl` first to populate the `URL_VERSION` metadata before `decorateResponse` reads it
- Assuming that a `null` version in the URL results in `setCacheDurationToMaximum()` instead of the default duration
- Not testing both paths (version match AND version mismatch) in the same test method

**Example (correct):**

```java
// Setup RequestCycle with a tester
BaseWicketTester tester = new BaseWicketTester();
RequestCycle requestCycle = ThreadContext.getRequestCycle();
Application.get().getResourceSettings().setDefaultCacheDuration(Duration.minutes(60));

try {
    // --- Test version MISMATCH ---
    // Simulate a URL with NO version parameter (or a wrong one)
    ResourceUrl url = new ResourceUrl("some-resource.txt", new PageParameters());
    strategy.undecorateUrl(url); // stores null/mismatched version in requestCycle metadata
    
    AbstractResource.ResourceResponse response = new AbstractResource.ResourceResponse();
    strategy.decorateResponse(response, new TestResource());
    
    // Should use default cache duration, not maximum
    assertEquals(Duration.minutes(60), response.getCacheDuration());
    assertEquals(WebResponse.CacheScope.PRIVATE, response.getCacheScope());
    
    // --- Test version MATCH ---
    requestCycle.setMetaData(IResourceCachingStrategy.URL_VERSION, TEST_RESOURCE_VERSION);
    
    response = new AbstractResource.ResourceResponse();
    strategy.decorateResponse(response, new TestResource());
    
    assertEquals(WebResponse.MAX_CACHE_DURATION, response.getCacheDuration());
    assertEquals(WebResponse.CacheScope.PUBLIC, response.getCacheScope());
} finally {
    tester.destroy();
}
```

**Example (incorrect — only tests happy path):**

```java
// BAD: Only tests version match, never tests what happens on mismatch
BaseWicketTester tester = new BaseWicketTester();
RequestCycle requestCycle = ThreadContext.getRequestCycle();
requestCycle.setMetaData(IResourceCachingStrategy.URL_VERSION, TEST_RESOURCE_VERSION);

AbstractResource.ResourceResponse response = new AbstractResource.ResourceResponse();
strategy.decorateResponse(response, new TestResource());

// Only checks the happy path — misses the bug entirely
assertEquals(WebResponse.MAX_CACHE_DURATION, response.getCacheDuration());
assertEquals(WebResponse.CacheScope.PUBLIC, response.getCacheScope());
// The bug: when version is missing/null, the code incorrectly sets max cache duration
```