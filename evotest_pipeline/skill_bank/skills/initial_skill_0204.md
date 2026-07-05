---
name: forward-attribute-request-uri-parsing
description: When a ServletWebRequest processes forwarded requests, the ForwardAttributes
  parser may return the wrong request URI if it fails to look up the javax.servlet.forward.request_uri
  attribute. This skill teaches TG to test forwarding attribute parsing with mock
  HttpServletRequest objects that have both request URI and forward attribute set.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- VALIDATION
- FORWARD_ATTRIBUTE_PARSING
- CONTEXT_RELATIVE_URL
test_pattern: PARAMETRIC_TEST
---

# forward-attribute-request-uri-parsing

## Instructions

# Forward Attribute Request URI Parsing

## Instructions

**WHEN** the TG encounters a `ForwardAttributes` class that parses forwarded request attributes from an `HttpServletRequest` (specifically `RequestDispatcher.FORWARD_REQUEST_URI` / `"javax.servlet.forward.request_uri"`) and computes a context-relative URL using `getContextRelativeUrl(uri, filterPrefix)`:

- **THEN** the TG should write a test that mocks an `HttpServletRequest` where:
  - `getRequestURI()` returns a non-forwarded URI like `"/context/some/other/url"` (the fallback)
  - `getAttribute("javax.servlet.forward.request_uri")` returns a forwarded URI like `"/context/some/forwarded/url"` (the expected value)
  - `getContextPath()` returns `"/context"`
  - A non-null `filterPrefix` (e.g., empty string `""`) is provided
- **THEN** the test should call `ForwardAttributes.of(request, filterPrefix)` then `forwardAttributes.getRequestUri()` (or `new ServletWebRequest(request, filterPrefix).getUrl().toString()`) 
- **THEN** the test should **assert that the returned URI equals the forwarded URI** (e.g., `"some/forwarded/url"` — context-relative), NOT the fallback `request.getRequestURI()` value
- **Common pitfalls:**
  - ❌ Testing only the case where `getAttribute("javax.servlet.forward.request_uri")` returns `null` (non-forwarded scenario) — this misses the bug entirely
  - ❌ Asserting the raw request URI instead of the context-relative URI — the returned value is relative to context path, not absolute
  - ❌ Using a mock that doesn't set both `getRequestURI()` and `getAttribute(forward.request_uri)` to different values — the bug is exactly that the wrong source is used
  - ❌ Not providing a `filterPrefix` parameter when constructing `ForwardAttributes` — the method signature requires it

**Correct test approach (pseudocode):**
```java
HttpServletRequest request = mock(HttpServletRequest.class);
when(request.getRequestURI()).thenReturn("/context/some/other/url");
when(request.getAttribute("javax.servlet.forward.request_uri")).thenReturn("/context/some/forwarded/url");
when(request.getContextPath()).thenReturn("/context");

ForwardAttributes attrs = ForwardAttributes.of(request, "");
// OR: ServletWebRequest swr = new ServletWebRequest(request, "");
String result = attrs.getRequestUri();
// OR: String result = swr.getUrl().toString();

assertEquals("some/forwarded/url", result);  // context-relative, not absolute
```

**Incorrect test approach (misses the bug):**
```java
// Only tests non-forwarded scenario — doesn't exercise the forward attribute path
when(request.getRequestURI()).thenReturn("/context/normal/url");
when(request.getAttribute("javax.servlet.forward.request_uri")).thenReturn(null);
ForwardAttributes attrs = ForwardAttributes.of(request, "");
assertEquals("normal/url", attrs.getRequestUri());  // works on both versions
```