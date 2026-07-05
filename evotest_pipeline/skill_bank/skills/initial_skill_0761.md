---
name: home-page-mapper-query-parameter-handling
description: When testing URL mappers that handle query parameters alongside path
  parameters, the TG should verify that query parameters do not interfere with the
  mapping of path parameters (like page parameters). This skill applies to request
  mapper implementations that use both query string and path segments.
code_tags:
- STATE_MUTATION
- BOUNDARY_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# home-page-mapper-query-parameter-handling

## Instructions

# HomePageMapper Query Parameter Handling

## Instructions

- WHEN the TG encounters a `HomePageMapper` (or any `IMapper` subclass that maps requests to page/page parameters) that both accepts a `Request` and extracts page parameters via `Url.getQueryParameters()` or parses path segments into indexed/named parameters
- THEN the TG should write a test that:
  1. Constructs a request that includes **both path parameters** (e.g., page parameters in the URL path) **and query parameters** (e.g., `?foo=bar`)
  2. Calls `mapRequest(request)` to obtain the `PageParameters`
  3. Asserts that the `PageParameters` contain the expected values **only** from the path segment, and that query parameters are **not** erroneously merged into the page parameters
  4. If the mapper extends `AbstractBookmarkableMapper` or `AbstractMapper`, verify that query parameters passed via the `Request` URL are **not** included in the `PageParameters` returned by `mapRequest`
- Common pitfall: testing only with query parameters or only with path parameters, but not with **both at the same time** — this misses the bug where query parameters silently bleed into page parameters
- Common pitfall: relying on the mapper's `resolveUrl` or `mapHandler` method alone — the bug manifests in `mapRequest` when query parameters are present in the request URL but should be ignored for page parameter resolution

**Correct example** (triggers the bug):
```java
@Test
public void mapRequestWithQueryParameters_DoesNotIncludeQueryParamsInPageParameters()
{
    HomePageMapper mapper = new HomePageMapper();
    Request request = new Request(new Url("?foo=bar")); // query param only
    PageParameters params = mapper.mapRequest(request).getPageParameters();
    assertThat("Query parameters must not appear in page parameters", 
               params.get("foo"), is(nullValue()));
}
```

**Incorrect example** (misses the bug):
```java
@Test
public void mapRequestReturnsPageParameters()
{
    HomePageMapper mapper = new HomePageMapper();
    // Only tests without query parameters — passes on buggy code too
    Request request = new Request(new Url());
    assertNotNull(mapper.mapRequest(request));
}
```