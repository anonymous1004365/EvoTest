---
name: redirect-url-preserves-query-string
description: When a method constructs a redirect URL using a base path plus a query
  string from the request, test that the query string is properly appended and the
  full URL is correct. This skill prevents missing query parameter handling in redirect
  scenarios.
code_tags:
- URL_HANDLING
- REDIRECT_HANDLING
test_pattern: STATE_TEST
---

# redirect-url-preserves-query-string

## Instructions

# Redirect URL Preserves Query String

## Instructions

- WHEN the TG encounters a `sendRedirect` method (e.g. `void sendRedirect(String url)`) that builds a redirect URL by combining a base path (e.g. `/redirect`) with a query string extracted from the request (e.g. `request.getQueryString()` returning `?key=value`)
- THEN the TG should write a test that:
  1. Creates a mock `HttpServletRequest` and/or `HttpServletResponse` (or use a test framework that simulates the HTTP request/response lifecycle).
  2. Sets up the request with a non-empty query string (e.g. `?foo=bar&baz=123`) that the redirect method must append.
  3. Calls `sendRedirect` on the response object (e.g. `servletResponse.sendRedirect(url)`) and verifies that the redirect URL passed to the underlying servlet response contains both the base path AND the full query string.
  4. Verifies that the query string of the redirect URL equals the original request's query string (e.g. `verify(response).sendRedirect("/redirect?foo=bar&baz=123")`).

- **Common pitfalls to avoid:**
  - Testing only with a `null` or empty query string — this will not reveal missing query string handling.
  - Only verifying the base path without checking the appended query string.
  - Forgetting to set the request's query string in the test setup.
  - Assuming that the servlet container handles query string encoding — test with both simple and encoded query parameter values.

### Example (correct):
```java
// Setup: create mock request with query string
HttpServletRequest request = mock(HttpServletRequest.class);
when(request.getQueryString()).thenReturn("foo=bar&baz=123");

// Call sendRedirect
servletResponse.sendRedirect("/redirect");

// Verify the redirect URL includes query string
verify(response).sendRedirect("/redirect?foo=bar&baz=123");
```

### Example (incorrect — missing query string check):
```java
// Problem: only verifies the base path, won't catch missing query string
servletResponse.sendRedirect("/redirect");
verify(response).sendRedirect("/redirect");
// This passes even if query string is silently dropped!
```