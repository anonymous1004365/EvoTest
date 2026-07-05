---
name: relative-url-bookmarkable-mapping
description: WHEN the TG encounters a URL mapper (like BookmarkableMapper) that handles
  relative URLs by comparing request URL segments against base URL segments, THEN
  it should test combinations where the request URL is missing the namespace prefix
  (e.g. 'bookmarkable/MyPage' instead of 'wicket/bookmarkable/MyPage') and the base
  URL has only 2 segments (e.g. 'wicket/page' or 'bookmarkable/MyPage').
code_tags:
- URL_PARSING
- NULL_CHECK
- RELATIVE_URL_RESOLUTION
test_pattern: STATE_TEST
---

# relative-url-bookmarkable-mapping

## Instructions

# Relative URL Bookmarkable Mapping

## Instructions

- WHEN the TG encounters a URL mapper class that uses both `request.getUrl()` and `request.getClientUrl()` to determine whether a relative request URL matches a known pattern (e.g., `BookmarkableMapper.matches()` checking `urlStartsWith` against base URL segments)
- THEN it should test URL scenarios where:
  - The **base URL** has **exactly 2 segments** (e.g., `[namespace, pageIdentifier]` like `["wicket", "page"]` or `[bookmarkableIdentifier]` like `["bookmarkable"]`)
  - The **request URL** has **at least 2 segments** and starts with the bookmarkableIdentifier (e.g., `["bookmarkable", "com.example.MyPage"]`)
  - The request URL is a **relative URL** meaning it does NOT start with the namespace/prefix that the absolute form would require
- The test should verify that the mapper's `mapRequest()` method returns a **non-null IRequestHandler** (e.g., `RenderPageRequestHandler`) rather than `null`
- The test should use `Url.parse()` with a string like `"bookmarkable/" + PAGE_CLASS_NAME` and create a custom `Request` that:
  - Overrides `getUrl()` to return the parsed relative URL
  - Overrides `getClientUrl()` to return a base URL like `Url.parse("wicket/page")` or `Url.parse("wicket/bookmarkable/" + PAGE_CLASS_NAME)`
  - Overrides `getLocale()` to return `Locale.getDefault()`
  - Overrides `getCharset()` to return `Charset.forName("UTF-8")`
- Common pitfalls to avoid:
  - Testing only absolute URLs (e.g., `"wicket/bookmarkable/com.example.MyPage"`) and missing relative URL scenarios
  - Forgetting that the base URL (`getClientUrl()`) matters for URL resolution — the mapper checks the base URL segments to decide if a relative URL matches
  - Omitting the `getLocale()`, `getCharset()`, `getUrl()`, and `getClientUrl()` overrides in the custom `Request` anonymous class
  - Not verifying that the handler is non-null before inspecting it (assert the handler exists, then check its type with `assertTrue(handler instanceof RenderPageRequestHandler)`)

### Example (correct):
```java
@Test
public void decode13()
{
    // baseUrl = 'wicket/page[?...]', requestUrl = 'bookmarkable/com.example.SomePage'
    final Url url = Url.parse(context.getBookmarkableIdentifier() + "/" + PAGE_CLASS_NAME);
    final Url baseUrl = Url.parse(context.getNamespace() + "/" + context.getPageIdentifier());

    Request request = new Request()
    {
        @Override
        public Url getUrl()
        {
            return url;
        }

        @Override
        public Url getClientUrl()
        {
            return baseUrl;
        }

        @Override
        public Locale getLocale()
        {
            return Locale.getDefault();
        }

        @Override
        public Charset getCharset()
        {
            return Charset.forName("UTF-8");
        }
    };
    IRequestHandler handler = encoder.mapRequest(request);
    assertNotNull("A handler should be resolved for relative url to a bookmarkable page url!", handler);
    assertTrue(handler instanceof RenderPageRequestHandler);
}
```

### Example (incorrect — missing baseUrl override):
```java
@Test
public void decode13_Wrong()
{
    // Only setting getUrl(), no getClientUrl() override
    final Url url = Url.parse("bookmarkable/" + PAGE_CLASS_NAME);
    IRequestHandler handler = encoder.mapRequest(getRequest(url));
    // This will fail because the mapper needs the client URL to determine if this is a relative URL match
    assertNotNull("A handler should be resolved", handler);
}
```