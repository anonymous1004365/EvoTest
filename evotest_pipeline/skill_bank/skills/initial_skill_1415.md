---
name: relative-url-to-bookmarkable-page
description: When a mapper uses base URL and request URL comparison to determine whether
  a request matches a pattern, the TG should test with a relative URL that is a valid
  bookmarkable page URL (e.g., "bookmarkable/com.example.MyPage") to ensure the mapper
  correctly resolves it. This skill catches bugs where relative URLs to bookmarkable
  pages fail to be matched.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- BOUNDARY_CHECK
- RELATIVE_URL_RESOLUTION
- VALIDATION
test_pattern: INTERACTION_TEST
---

# relative-url-to-bookmarkable-page

## Instructions

# Relative URL to Bookmarkable Page Resolution

## Instructions

- WHEN the TG encounters a URL mapper (like `BookmarkableMapper`) that implements a `matches(Request)` or `parseRequest(Request)` method comparing `request.getUrl()` (relative) against `request.getClientUrl()` (base URL) to determine if a request matches bookmarkable URL patterns
- THEN the TG should write a test that:
  1. Constructs a `Url` representing a relative bookmarkable URL such as `"bookmarkable/" + MockPage.class.getName()` (without the namespace prefix)
  2. Creates a `Request` from this URL with the appropriate `getClientUrl()` (e.g., `Url.parse("wicket/bookmarkable/" + MockPage.class.getName())` as the base URL) to simulate the browser making a relative request
  3. Calls `mapper.mapRequest(request)` and asserts that a non-null handler is returned (e.g., `assertNotNull(handler, "A handler should be resolved for relative url to a bookmarkable page url!")`)
  4. Verifies the handler is of type `RenderPageRequestHandler` using `assertThat(handler, instanceOf(RenderPageRequestHandler.class))`
  5. Verifies the resolved page class is the expected class using `assertEquals(PAGE_CLASS_NAME, ((RenderPageRequestHandler)handler).getPage().getClass().getName())`

- Common pitfalls to avoid:
  - Testing only absolute URLs (with namespace prefix like "wicket/bookmarkable/...") but not relative URLs that omit the namespace prefix
  - Testing only with a relative URL that is incomplete (e.g., just "wicket/bookmarkable") — the TG should test the specific case where the relative URL starts with the bookmarkable identifier and has a valid page class segment after it
  - Forgetting to set up the `getClientUrl()` on the mock request to provide the base URL context
  - Assuming the mapper returns a handler without checking the result type — always verify the handler is of the expected type

## Example

**Correct test:**
```java
@Test
public void decode13()
{
    // base URL = "wicket/bookmarkable/org.apache.wicket.MockPage"
    // relative request URL = "bookmarkable/org.apache.wicket.MockPage"
    Url url = Url.parse("bookmarkable/" + PAGE_CLASS_NAME);
    IRequestHandler handler = encoder.mapRequest(getRequest(url));
    
    assertNotNull("A handler should be resolved for relative url to a bookmarkable page url!", handler);
    assertThat(handler, instanceOf(RenderPageRequestHandler.class));
    IRequestablePage page = ((RenderPageRequestHandler)handler).getPage();
    assertEquals(PAGE_CLASS_NAME, page.getClass().getName());
}
```

**Incorrect test (would miss the bug):**
```java
@Test
public void decode13()
{
    // Only tests absolute URL — does not test relative URL without namespace prefix
    Url url = Url.parse("wicket/bookmarkable/" + PAGE_CLASS_NAME);
    IRequestHandler handler = encoder.mapRequest(getRequest(url));
    assertThat(handler, instanceOf(RenderPageRequestHandler.class));
}
```