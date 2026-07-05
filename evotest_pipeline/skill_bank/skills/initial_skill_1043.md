---
name: filter-path-prefix-stripping
description: When building a request URL from forwarded/error request attributes (javax.servlet.forward.request_uri,
  javax.servlet.error.request_uri), the filter path prefix must be correctly stripped
  by calling substring(filterPath.length()) only after verifying the URI actually
  starts with filterPath. Tests should exercise the prefix removal logic with filter
  paths like "/filterPath" and URIs like "/filterPath/any/source/of/error".
code_tags:
- STATE_MUTATION
- VALIDATION
- ARRAY_INDEX_ACCESS
- FILTER_PATH_PREFIX_STRIPPING
- ARGUMENT_VALIDATION
test_pattern: STATE_TEST
---

# filter-path-prefix-stripping

## Instructions

# Filter Path Prefix Stripping

## Instructions

### WHEN the TG encounters:
A `ServletWebRequest` (or similar servlet request wrapper) building URLs from `javax.servlet.forward.*` or `javax.servlet.error.*` request attributes — specifically when calling methods like `getRequestUri()` or `getUrl()` that compute a URI by stripping a **filter path prefix** (e.g. `ServletWebRequest.getRequestUri()`, `wrapRequest()`).

### THEN the TG should:

1. **Identify the filter path prefix stripping logic** — look for code that computes a `filterPath` (e.g. via `getFilterPath()`) and then removes it from a URI string using `uri.substring(filterPath.length())`.

2. **Test with a filter path that is a non-trivial prefix** — for example, set up a request where `getFilterPath()` returns `"/filterPath"` and the request attribute `javax.servlet.forward.request_uri` (or `javax.servlet.error.request_uri`) is `"/filterPath/any/source/of/error"`. The expected result after stripping should be `"/any/source/of/error"`.

3. **Verify the correct prefix removal** — the test must assert that the filter path prefix is removed correctly and the remainder (starting from `/`) is preserved. For the buggy version, the filter path is **not** stripped, producing `"/filterPath/any/source/of/error"` instead of `"/any/source/of/error"`.

4. **Use mock servlet request attributes** — since the logic depends on `javax.servlet.forward.*` and `javax.servlet.error.*` attributes, the test should set up a `MockHttpServletRequest` with the appropriate `getAttribute(...)` values and a mock `FilterConfig` to provide the filter path.

### Common pitfalls to avoid:

- **Only testing without a filter path** — the bug manifests only when there IS a filter path prefix that should be stripped. Testing only the "no filter path" case (empty string or null) will NOT catch this bug.
- **Testing direct getAttribute value without considering the stripping logic** — the test must look at the FINAL computed URI, not just what's stored in the attribute.
- **Confusing the test with unrelated filter/error handling** — focus specifically on the scenario: a forward/error request attribute URI starts with the filter path, and the code should remove that prefix.

### Example (correct test):

```java
@Test
public void testFilterPathStripping() {
    // Setup request with filter path prefix
    MockHttpServletRequest request = new MockHttpServletRequest();
    request.setAttribute(FilterConfig.class.getName(), ...); // filter path = "/filterPath"
    request.setAttribute("javax.servlet.forward.request_uri", "/filterPath/any/source/of/error");
    
    ServletWebRequest swr = new ServletWebRequest(request, ...);
    String result = swr.getRequestUri(); // or whatever method computes the URL
    
    // Expected: filter path stripped
    assertEquals("/any/source/of/error", result);
}
```

### Example (incorrect test that misses the bug):

```java
@Test
public void testFilterPathStripping() {
    // Setup WITHOUT filter path prefix — will NOT trigger the bug
    MockHttpServletRequest request = new MockHttpServletRequest();
    request.setAttribute("javax.servlet.forward.request_uri", "/any/source/of/error");
    
    ServletWebRequest swr = new ServletWebRequest(request, ...);
    String result = swr.getRequestUri();
    
    // This passes even with the buggy code
    assertEquals("/any/source/of/error", result);
}
```