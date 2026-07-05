---
name: absolute-url-rendering-with-semicolons
description: Teaches how to test URL rendering methods that preserve absolute URLs
  when the base URL contains path segments with semicolons. Apply when testing servlet
  response URL encoding where the request URL contains path parameters.
code_tags:
- STATE_MUTATION
- NULL_CHECK
- VALIDATION
- ABSOLUTE_URL_RENDERING
test_pattern: STATE_TEST
---

# absolute-url-rendering-with-semicolons

## Instructions

# Absolute URL Rendering with Semicolons in Path

## Instructions

- WHEN the TG encounters a method that renders or encodes absolute URLs (e.g., `renderFullUrl`, `encodeAbsoluteUrl`, `renderRelativeUrl` in `UrlRenderer` or `ServletWebResponse`) and the method processes a base URL / request URL that may contain path segments
- THEN the TG should test rendering URLs where the base URL's path contains semicolons (path parameters like `;foo`), verifying that the rendered output preserves the absolute base URL **as an absolute URL** and does NOT collapse it to a relative path like `../`
  - Example: base URL = `http://localhost:8080/path;foo`, relative URL = `/path;foo` → expected output = `http://localhost:8080/path;foo`, NOT `../path;foo`
  - The TG should test that `encodeAbsoluteUrl(HttpServletRequest, URL)` in `ServletWebResponse` returns the correct absolute URL string when the request URL has path parameters (semicolons)
  - The test should simulate a request where `getRequestURL()` returns something like `http://localhost:8080/path;foo` and the URL to encode is `/path;foo`
- WHEN the TG writes this test, it should assert that the returned URL equals the full absolute URL (e.g., `"http://localhost:8080/path;foo"`) — on the buggy version this returns `"../path;foo"` which is wrong
- Common pitfalls:
  - Testing only URLs with clean paths (no semicolons) — this misses the bug entirely
  - Testing only the `UrlRenderer` in isolation without considering how `ServletWebResponse` processes the request URL
  - Assuming path parameters (semicolons) are stripped or normalized before URL rendering — they are not, and the rendering must handle them correctly
  - Testing with a relative base URL when the bug only manifests with absolute base URLs containing semicolons

### Correct test approach (example):
```java
@Test
public void encodeAbsoluteUrl_withSemicolonInPath_returnsAbsoluteUrl() {
    // Setup request with URL containing semicolon path parameter
    HttpServletRequest request = mock(HttpServletRequest.class);
    when(request.getRequestURL()).thenReturn(new StringBuffer("http://localhost:8080/path;foo"));
    when(request.getContextPath()).thenReturn("");
    
    ServletWebResponse response = new ServletWebResponse(request, ...);
    String result = response.encodeAbsoluteUrl("/path;foo");
    
    assertEquals("http://localhost:8080/path;foo", result);
}
```

### Incorrect approach (missing the bug):
```java
@Test
public void encodeAbsoluteUrl_cleanPath_returnsAbsoluteUrl() {
    // Only tests clean paths — won't catch the semicolon bug
    HttpServletRequest request = mock(HttpServletRequest.class);
    when(request.getRequestURL()).thenReturn(new StringBuffer("http://localhost:8080/path"));
    when(request.getContextPath()).thenReturn("");
    
    ServletWebResponse response = new ServletWebResponse(request, ...);
    String result = response.encodeAbsoluteUrl("/path");
    
    assertEquals("http://localhost:8080/path", result);
}
```