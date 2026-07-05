---
name: url-path-segment-validation-for-mapper-matching
description: When a URL mapper uses both the request URL and the client base URL to
  determine if a request matches, the TG should test edge cases where the request
  URL has fewer segments than the base URL, particularly when the request URL contains
  only the page identifier without the namespace prefix.
code_tags:
- VALIDATION
- PATH_PARSING_VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# url-path-segment-validation-for-mapper-matching

## Instructions

# URL Path Segment Validation for Mapper Matching

## Instructions

- WHEN the TG encounters a URL mapper class (like `PageInstanceMapper`) that uses both `request.getUrl()` and `request.getClientUrl()` (base URL) in its `matches()` method to decide whether to handle a request
- THEN the TG should test scenarios where the request URL has FEWER path segments than the base/client URL, especially:
  - **Request URL** = `"page?4"` (single segment: `["page"]`), **Client URL** = `"wicket/page"` (two segments: `["wicket", "page"]`)
  - This exercises the `urlStartsWith(baseUrl, namespace, pageIdentifier) && urlStartsWith(url, pageIdentifier)` branch in the `matches()` method
  - The TG should verify that a valid `IRequestHandler` (specifically `RenderPageRequestHandler` or `ListenerRequestHandler`) is returned, not `null`
- WHEN the TG is testing the `isNotPageInstanceUrl()` guard method (which filters URLs by segment count > 2 or segments after the pageIdentifier)
- THEN the TG should verify that the guard correctly allows URLs where the request has fewer segments than the base URL through to the matching logic, and that the matching logic correctly matches them
- **Common pitfalls**:
  - Testing only URLs where the request and base URL have the same number of segments (e.g., both have `["wicket", "page"]`)
  - Assuming that when request URL segments don't include the namespace prefix, the mapper always returns null
  - Testing with mocked requests that don't properly exercise the base URL matching logic
  - Not constructing a custom `Request` subclass that returns different values for `getUrl()` vs `getClientUrl()`

### Example (correct)
```java
@Test
public void decode9()
{
    final Url url = Url.parse("page?4");

    Request request = new Request()
    {
        @Override
        public Url getUrl() { return url; }

        @Override
        public Locale getLocale() { return null; }

        @Override
        public Charset getCharset() { return Charset.forName("UTF-8"); }

        @Override
        public Url getClientUrl() { return Url.parse("wicket/page"); }

        @Override
        public Object getContainerRequest() { return null; }
    };

    IRequestHandler handler = encoder.mapRequest(request);
    IRequestablePage page = ((IPageRequestHandler)handler).getPage();
    checkPage(page, 4);
}
```

### Example (incorrect - only testing same-length URL paths)
```java
// BAD: Only tests the case where request URL has namespace prefix
// This misses the bug where request URL has fewer segments than base URL
@Test
public void decode_only_namespace_case()
{
    Url url = Url.parse("wicket/page?4");
    IRequestHandler handler = encoder.mapRequest(getRequest(url));
    RenderPageRequestHandler h = (RenderPageRequestHandler)handler;
    checkPage(h.getPage(), 4);
}
```