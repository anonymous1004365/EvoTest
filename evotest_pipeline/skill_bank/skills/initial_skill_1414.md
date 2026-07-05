---
name: inner-class-page-mapping
description: Use this skill when building or testing URL mappers that map page classes
  to URL segments, especially when those page classes are inner/nested classes. The
  bug was that PackageMapper.buildUrl used getSimpleName() which only returns the
  innermost class name for inner classes (e.g. "InnerPage"), losing the outer class
  structure needed for correct URL resolution.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# inner-class-page-mapping

## Instructions

# Inner Class Page Mapping

## Instructions

- WHEN the TG encounters a URL mapper (like `PackageMapper`) that calls `pageClass.getSimpleName()` to produce a URL segment for a page class
- THEN the TG should test with an inner/nested page class (a static inner class that extends a page/component class, e.g. `OuterPage.InnerPage extends MockPage`)
  - Create a handler with the inner page class (e.g., `new PageProvider(OuterPage.InnerPage.class, new PageParameters())`)
  - Call `mapper.mapHandler(handler)` to get the URL
  - Verify the URL segment uses the **fully qualified class name relative to the package** (e.g., `"PackageMapperTest$OuterPage$InnerPage"`), NOT just `getSimpleName()` (which would return just `"InnerPage"`)
  - Also verify that decoding the produced URL via `mapper.mapRequest(getRequest(Url.parse(...)))` returns a non-null handler (the round-trip works)
- WHEN the TG tests URL parsing/decoding for inner classes
  - THEN verify the mapper correctly resolves a URL containing `$`-separated inner class paths (e.g., `"PackageMapperTest$OuterPage$InnerPage"`) back to the correct `Class<? extends IRequestablePage>`
- Common pitfalls:
  - Testing only with top-level page classes (e.g., `MockPage`) — this misses the inner class bug entirely
  - Assuming `getSimpleName()` is sufficient for class-to-URL mapping — it fails for inner classes because `javax.swing.SwingPaintEventDispatcher$PaintEventDispatcher` (hypothetical) would map incorrectly
  - Not verifying the round-trip (encode → decode produces the same class) for inner classes
  - Forgetting that inner class names use `$` as separator in their fully qualified class name (e.g., `org.apache.wicket.request.mapper.PackageMapperTest$OuterPage$InnerPage`)

### Correct Example (simulating the fix behavior)

```java
// Test encoding of an inner class page
public void testEncodeInnerClass()
{
    // OuterPage.InnerPage is a static inner class extending MockPage
    PageProvider provider = new PageProvider(OuterPage.InnerPage.class, new PageParameters());
    provider.setPageSource(context);
    IRequestHandler handler = new BookmarkablePageRequestHandler(provider);
    Url url = encoder.mapHandler(handler);
    // Should use fully qualified name relative to package, e.g. "PackageMapperTest$OuterPage$InnerPage"
    assertEquals("PackageMapperTest$OuterPage$InnerPage", url.toString());
    
    // Round-trip: decode the URL back
    Url requestUrl = Url.parse("PackageMapperTest$OuterPage$InnerPage");
    IRequestHandler decoded = encoder.mapRequest(getRequest(requestUrl));
    assertNotNull("Inner class page should be decodable", decoded);
    assertTrue(decoded instanceof RenderPageRequestHandler);
    assertEquals(OuterPage.InnerPage.class, ((RenderPageRequestHandler)decoded).getPage().getClass());
}
```

### Incorrect Example (what would pass the buggy version but shouldn't)

```java
// BAD: Only tests top-level classes, misses the inner class bug
public void testEncodeMockPage()
{
    PageProvider provider = new PageProvider(MockPage.class, new PageParameters());
    provider.setPageSource(context);
    IRequestHandler handler = new BookmarkablePageRequestHandler(provider);
    Url url = encoder.mapHandler(handler);
    assertEquals("MockPage", url.toString()); // This works even in buggy version
}
```