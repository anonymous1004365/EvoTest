---
name: package-mapper-indexed-parameter-count
description: WHEN testing PackageMapper.parseRequest for hybrid URLs (page class +
  pageId + indexed parameters), THEN verify that indexed page parameters are correctly
  extracted. This skill addresses the bug where indexed parameters on hybrid URLs
  were being double-counted or lost during extraction.
code_tags:
- PATH_PARSING
- STRING_MANIPULATION
- BOUNDARY_CHECK
test_pattern: STATE_TEST
---

# package-mapper-indexed-parameter-count

## Instructions

# PackageMapper Indexed Parameter Count on Hybrid URLs

## Instructions

WHEN the TG encounters code that uses `PackageMapper.parseRequest()` to parse a URL containing a hybrid request (page class + pageId + indexed parameters + query parameters), THEN the TG should write a test that verifies the exact count of indexed and named parameters on the resulting PageParameters object.

Specifically:
- WHEN testing `PackageMapper.mapRequest()` with URLs in the format `mount/path/PageClassName/indexedParam1/indexedParam2?pageId&namedKey1=value1&namedKey2=value2`
- THEN the test MUST assert:
  1. The returned handler is an instance of `RenderPageRequestHandler`
  2. `page.getPageParameters().getIndexedCount()` equals the expected number of indexed parameters (e.g., `assertEquals(2, p.getIndexedCount())` for `/i1/i2`)
  3. `page.getPageParameters().getNamedKeys().size()` equals the expected number of named parameters (e.g., `assertEquals(2, p.getNamedKeys().size())` for `a=b&b=c`)
- The test MUST set a page source on the PageProvider: `((PageProvider) h.getPageProvider()).setPageSource(context)` before calling `h.getPage()`

Common pitfalls to avoid:
- Testing only the handler type and page class without checking parameter counts — parameters may be silently dropped or double-counted
- Forgetting to call `setPageSource(context)` on the PageProvider, which causes the test to fail with a NullPointerException or incorrect page resolution
- Testing only String type URL components — the bug manifests specifically with hybrid URLs that combine pageId and indexed parameters
- Assuming that if the handler type is correct, all parameters are properly parsed

Correct test example:
```java
@Test
public void decode4()
{
    Url url = Url.parse(MOUNT_PATH + '/' + PAGE_CLASS_NAME + "/i1/i2?15&a=b&b=c");
    IRequestHandler handler = encoder.mapRequest(getRequest(url));

    assertThat(handler, instanceOf(RenderPageRequestHandler.class));
    RenderPageRequestHandler h = (RenderPageRequestHandler) handler;
    ((PageProvider) h.getPageProvider()).setPageSource(context);
    IRequestablePage page = h.getPage();
    checkPage(page, 1);

    PageParameters p = page.getPageParameters();
    assertEquals(2, p.getIndexedCount());     // /i1 and /i2
    assertEquals(2, p.getNamedKeys().size()); // a=b and b=c
}
```

Incorrect test (would miss the bug):
```java
@Test
public void decode4()
{
    Url url = Url.parse(MOUNT_PATH + '/' + PAGE_CLASS_NAME + "/i1/i2?15&a=b&b=c");
    IRequestHandler handler = encoder.mapRequest(getRequest(url));
    assertThat(handler, instanceOf(RenderPageRequestHandler.class));
    // Does NOT verify parameter counts — would pass even if parameters are corrupted
}
```