---
name: empty-url-rendering-with-absolute-path
description: Use this skill when testing URL rendering logic that must handle empty
  URLs (blank strings) correctly, as some implementations may fail to render them
  while producing valid output for non-empty URLs. Test with empty string alongside
  real URLs to catch missing branch coverage.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# empty-url-rendering-with-absolute-path

## Instructions

# Empty URL Rendering with Absolute Path

## Instructions

- WHEN the test generator encounters a URL renderer class (like `UrlRenderer`) that provides methods to render relative or absolute URLs from a base URL, and there exists a `renderUrl(Url)` method
- THEN it should **include an empty/blank URL `""` as a test case** alongside valid non-empty URLs, because the renderer may throw errors or produce wrong output for empty input even though all non-empty cases pass
- WHEN testing `renderUrl(Url.parse(""))` or similar empty-URL input, verify that:
  - The method does **not** throw a `StringIndexOutOfBoundsException`, `IndexOutOfBoundsException`, or `NullPointerException`
  - The returned String is either a valid relative URL (like `""` or `"."`) or a valid absolute URL depending on context
  - Test cases should use `Assert.assertEquals()` or JUnit 5 `assertEquals()` with the expected rendered result
- Common pitfalls to avoid:
  - **Testing only with non-empty URL strings** (e.g., `"some/path"`, `"http://example.com"`) — this leaves the empty-string branch uncovered
  - Assuming that because the method works for most inputs, it will handle the empty-string edge case correctly
  - Only testing the happy path where the base URL and rendered URL have the same number of segments — the empty URL can cause issues in `removeCommonPrefixes()` or segment iteration logic

## Example

For a class like:
```java
public class UrlRenderer {
    public String renderUrl(final Url url) { ... }
}
```

### Correct test approach (catches the bug):
```java
@Test
public void renderEmptyUrl()
{
    UrlRenderer renderer = new UrlRenderer(Url.parse("some/context/path"));
    // Empty URL should be handled without exception
    String result = renderer.renderUrl(Url.parse(""));
    // Verify the result is reasonable (depending on spec)
    assertNotNull(result);
}
```

### Incorrect test approach (misses the bug):
```java
@Test
public void renderNonEmptyUrl()
{
    UrlRenderer renderer = new UrlRenderer(Url.parse("some/context/path"));
    String result = renderer.renderUrl(Url.parse("other/path"));
    assertEquals("../../other/path", result);
}
```

The incorrect approach only tests non-empty URLs, which may all pass while the empty-URL case throws an exception or returns a malformed URL.