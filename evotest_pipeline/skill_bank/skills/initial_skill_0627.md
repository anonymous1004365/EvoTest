---
name: bookmarkable-mapper-path-parameter-sanitization
description: When parsing bookmarkable URLs with matrix/path parameters (e.g., ";something=else"
  appended to the class name segment), the TG should test that the mapper strips these
  parameters from the class name before resolving the page class. This prevents ClassNotFoundException
  when users append parameters like ";something=else" to bookmarkable URLs.
code_tags:
- URL_SEGMENT_VALIDATION
test_pattern: STATE_TEST
---

# bookmarkable-mapper-path-parameter-sanitization

## Instructions

# Bookmarkable Mapper Path Parameter Sanitization

## Instructions

- WHEN the TG encounters a `BookmarkableMapper.parseRequest(Request)` or `AbstractComponentMapper.cleanClassName(String)` method that processes a URL segment as a fully qualified class name (e.g., `segments.get(2)` or `segments.get(1)` where the segment value is expected to be something like `org.apache.wicket.MockPage`)

- THEN the TG should write a test that verifies the class name segment is properly sanitized when it contains matrix/path parameter syntax (i.e., a semicolon `;` followed by parameters). The bug is that in `BookmarkableMapper.parseRequest()`, the raw `className` segment (e.g., `"org.apache.wicket.MockPage;something=else"`) is passed directly to `getPageClass(className)` WITHOUT stripping the `;something=else` part first. The fix is in `AbstractComponentMapper.cleanClassName(String)` which uses `Strings.beforeFirst(className, ';')` to strip path parameters — but this method is NOT called in `BookmarkableMapper.parseRequest()`. The test should:

  1. Create a `Url` with a segment like `"wicket/bookmarkable/org.apache.wicket.MockPage;something=else"` (use `Url.parse(...)`)
  2. Call `mapper.mapRequest(getRequest(url))`
  3. Verify the handler is a `RenderPageRequestHandler` (not null and not an error)
  4. Verify the resolved page class equals `MockPage.class.getName()` — i.e., the `;something=else` part is stripped
  5. Verify page parameters are empty (no indexed or named parameters from the `;something=else` part)

- Common pitfalls:
  - Testing only clean URLs without any path parameters — the TG should specifically test with `;param=value` appended to the class name segment
  - Assuming `getPageClass()` internally handles semicolon stripping — it does NOT; the stripping must happen in `cleanClassName()` before `getPageClass()` is called
  - Testing with a semicolon but without the `=` sign (e.g., just `;something`) — path parameters typically use `;key=value` syntax, but the fix uses `Strings.beforeFirst(className, ';')` which strips everything after the first `;`, so both forms should work

### Example (correct test — matches the triggering test `decodePageClassWithPathParameters`):

```java
@Test
public void decodePageClassWithPathParameters()
{
    String pageClassName = MockPage.class.getName();
    Url url = Url.parse("wicket/bookmarkable/" + pageClassName + ";something=else");
    IRequestHandler handler = encoder.mapRequest(getRequest(url));

    assertTrue(handler instanceof RenderPageRequestHandler);
    IRequestablePage page = ((RenderPageRequestHandler)handler).getPage();
    assertEquals(pageClassName, page.getClass().getName());
    assertEquals(0, page.getPageParameters().getIndexedCount());
    assertTrue(page.getPageParameters().getNamedKeys().isEmpty());
}
```

### Example (incorrect test — only tests clean URLs, misses the bug):

```java
// BAD: Only tests clean URLs without path parameters
@Test
public void decode1()
{
    Url url = Url.parse("wicket/bookmarkable/" + MockPage.class.getName());
    IRequestHandler handler = encoder.mapRequest(getRequest(url));
    assertThat(handler, instanceOf(RenderPageRequestHandler.class));
    // This passes even on buggy code — doesn't catch the path parameter issue
}
```

### Explanation
The bug (WICKET-5500) is that `BookmarkableMapper.parseRequest()` extracts the class name from URL segments (e.g., `"org.apache.wicket.MockPage;something=else"`) and passes it directly to `getPageClass(className)` without sanitization. The `cleanClassName()` method in `AbstractComponentMapper` already handles stripping `;...` using `Strings.beforeFirst(className, ';')`, but `parseRequest()` does not call it. Without the fix, `getPageClass()` tries to resolve the literal string `"org.apache.wicket.MockPage;something=else"` as a class name, which fails with a `ClassNotFoundException` or returns null. The test must specifically use a URL with `;` path parameters appended to the class name segment to verify the sanitization.