---
name: context-relative-url-construction
description: When constructing context-relative URLs from forward/error request attributes,
  the URL must account for servlet path, path info, query string, and special cases
  like root context paths. This skill helps write tests that catch incorrect URL construction
  logic.
code_tags:
- NULL_CHECK
- VALIDATION
- BOUNDARY_CHECK
- CONTEXT_RELATIVE_URL
test_pattern: PARAMETRIC_TEST
---

# context-relative-url-construction

## Instructions

# Context-Relative URL Construction

## Instructions

- WHEN the TG encounters code that constructs a context-relative URL from an absolute URL (e.g., from `ErrorAttributes` or `ForwardAttributes`), by extracting the servlet path, path info, and query string from an `HttpServletRequest`
- THEN it should write **parametrized tests** that simulate different combinations of:
  - `getServletPath()` returning values like `""`, `"/"`, `"/app"`, `"/app/"` 
  - `getPathInfo()` returning values like `null`, `""`, `"/detail"`, `"/detail/"`
  - `getQueryString()` returning values like `null`, `""`, `"id=1"`, `"key=val&foo=bar"`
  - A `getContextPath()` returning values like `""`, `"/"`, `"/myapp"`, `"/myapp/"`
- The test should verify that the resulting constructed URL is correct even for edge cases like:
  - Context path is `""` or `"/"` (root context)
  - Servlet path is `"/"` (default servlet mapping)
  - Path info is `null` (no path info)
  - Query string is `null` or empty (no query params)
- Common pitfalls to avoid:
  - Testing only with non-empty, simple values (e.g., servletPath=`"/app"`, pathInfo=`"/detail"`, queryString=`"id=1"`) — this misses edge cases with empty/root paths
  - Not testing combinations where servletPath is empty string `""` and contextPath is `""` simultaneously — this can produce URLs starting with `//` or missing leading `/`
  - Assuming `getContextPath()` never returns `""` — it does for root-deployed applications
  - Not verifying the URL for forward attributes (`ForwardAttributes`) separately from error attributes (`ErrorAttributes`), as they may have different construction logic
- The test should expect the correctly constructed URL string and fail (produce wrong URL) on the buggy version while passing on the fixed version

### Example (Correct)

```java
@ParameterizedTest
@CsvSource({
    // contextPath, servletPath, pathInfo, queryString, expectedUrl
    "'',          '/app',       '/detail',   'id=1',      '/app/detail?id=1'",
    "'/',         '/app/',      '/detail/',  '',          '/app/detail/'",
    "'/myapp',    '',           '/detail',   'key=val',   '/myapp/detail?key=val'",
    "'',          '/',          'detail',    null,        '//detail'",
    "'/myapp',    '/',          null,        null,        '/myapp/'",
    "'',          '/app',       null,        null,        '/app'",
})
void testContextRelativeUrlConstruction(
    String contextPath, String servletPath, String pathInfo, 
    String queryString, String expectedUrl) {
    // setup mock request with these values
    // construct the URL using the method under test
    // assertEquals(expectedUrl, actualUrl);
}
```

### Example (Incorrect)

```java
// BAD: Only tests one simple case, misses all edge scenarios
@Test
void testContextRelativeUrl() {
    // Only tests the happy path
    String result = buildUrl("/myapp", "/detail", "id=1");
    assertEquals("/myapp/detail?id=1", result);
}
```