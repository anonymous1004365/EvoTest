---
name: caching-strategy-empty-filename
description: When the caching strategy returns an empty or null filename, the resource
  mapper should handle it gracefully instead of throwing an exception about an empty
  name. Use this skill when testing resource caching decoration/undecoration logic.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- VALIDATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# caching-strategy-empty-filename

## Instructions

# Caching Strategy Empty Filename Handling

## Instructions

WHEN the TG encounters code that calls a caching strategy's `undecorateUrl(ResourceUrl)` method inside a resource mapper (e.g., `removeCachingDecoration(Url, PageParameters)` in `ResourceMapper`) and the result is a `ResourceUrl` object whose `getFileName()` returns an empty string or `null`:

- THEN the TG should write a test that simulates a caching strategy returning an empty filename and verify that the mapper throws an `IllegalStateException` (or similar appropriate exception) with a message containing "caching strategy returned empty name for Name:"
- Include concrete types: `FilenameWithVersionResourceCachingStrategy` or a custom `IResourceCachingStrategy` implementation, `Url`, `PageParameters`, `ResourceUrl`
- The test should create a `Url` object with mount segments, encode a scenario where the caching strategy returns a `ResourceUrl` with an empty filename (e.g., set it to `""`), and then call the method that processes the URL through the caching strategy

**Common pitfalls to avoid:**
- Testing only the normal case where the caching strategy returns a valid filename — the bug occurs specifically when the filename is empty
- Forgetting that `undecorateUrl` wraps the result in a `ResourceUrl` that could have an empty `fileName` field — the issue is in the caller's handling of that result
- Testing at the wrong level (e.g., testing `FilenameWithVersionResourceCachingStrategy` in isolation instead of testing how `ResourceMapper.removeCachingDecoration` handles the result)

**Correct example:**
```java
@Test
public void requestWithEmptyFilename()
{
    ResourceMapper mapper = new ResourceMapper("test", resourceReference);
    // ... setup request with empty filename scenario ...
    // Expect IllegalStateException with message about empty name
}
```

**Incorrect example (would miss the bug):**
```java
@Test
public void requestWithValidFilename()
{
    // This test passes even on the buggy version because only the empty filename case fails
    ResourceMapper mapper = new ResourceMapper("test", resourceReference);
    // ... setup with valid filename ...
    // No exception expected
}
```