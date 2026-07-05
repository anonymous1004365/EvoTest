---
name: url-relative-check-with-query-params
description: WHEN testing URL relative/absolute detection logic that uses regex `^\w+\:\/\/.*`,
  THEN test URLs with scheme-like strings (e.g., "http://") appearing in query parameters
  to avoid false negatives where the regex matches the query string instead of the
  URL scheme.
code_tags:
- VALIDATION
- NULL_CHECK
- URL_IS_RELATIVE
test_pattern: PARAMETRIC_TEST
---

# url-relative-check-with-query-params

## Instructions

# URL Relative Check Must Handle Scheme-Like Strings in Query Parameters

## Instructions

- WHEN the test generator encounters a method like `UrlUtils.isRelative(String url)` that uses a regex pattern such as `^\\w+\\:\\/\\/.*` to determine if a URL is absolute
- THEN it must test with URLs that contain `://`-like patterns (e.g., `http://`, `https://`) inside query parameters, not just as the URL scheme
- Specifically, test a URL like `"./mypage?return=http://example.com"` — the method should return `true` (relative) because the URL starts with `./`, but the regex `^\\w+\\:\\/\\/.*` matches `http://example.com` in the query string because `.*` is greedy and the whole string matches the pattern
- The test must assert that `UrlUtils.isRelative("./mypage?return=http://example.com")` returns `true` (URL is relative even though it contains `://` in a query parameter)
- Also test URLs with `https://` or `ftp://` in query parameters appended to a relative path (e.g., `"./path?url=https://other.com"`)
- Common pitfall: Testing only simple URLs like `"http://example.com"` (absolute) vs `"/foo"` (absolute) vs `"./foo"` (relative), without testing the boundary case where `://` appears inside a query parameter of a relative URL. The regex `^\\w+\\:\\/\\/.*` will match the entire string if `://` appears anywhere after start, causing the method to return `false` (absolute) instead of `true` (relative).

**Correct test example:**
```java
@Test
public void isRelative_withSchemeLikeInQueryParam() {
    // relative URL with "http://" in query param must still be relative
    assertTrue("URL with scheme-like pattern in query param should be relative",
        UrlUtils.isRelative("./mypage?return=http://example.com"));
    assertTrue("URL with https:// in query param should be relative",
        UrlUtils.isRelative("./path/path2?param1=https://evil.com"));
}
```

**Wrong test that misses the bug:**
```java
@Test
public void isRelative() {
    assertTrue(UrlUtils.isRelative("./mypage"));
    assertFalse(UrlUtils.isRelative("http://example.com"));
    // Missing: ./mypage?return=http://example.com — this would FAIL on buggy version
}
```