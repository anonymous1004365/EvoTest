---
name: relative-url-resolution-with-no-segments
description: WHEN testing URL resolution logic (resolveRelative) with a base URL that
  has no path segments (e.g., query-only URLs like "?foo=bar"), THEN test that resolving
  a relative URL does not cause an ArrayIndexOutOfBoundsException and correctly replaces
  the base's query parameters with the relative URL's components.
code_tags:
- BOUNDARY_CHECK
- NULL_CHECK
- STATE_MUTATION
test_pattern: STATE_TEST
---

# relative-url-resolution-with-no-segments

## Instructions

# Relative URL Resolution With No Segments In Base

## Instructions

- WHEN the TG encounters the `resolveRelative(Url)` method on the `Url` class (org.apache.wicket.request.Url), specifically code that accesses `segments.get(segments.size() - 1)` or similar index-based operations on the segments list
- THEN it MUST test the edge case where the base `Url` has **zero path segments** (e.g., parsed from a query-only URL like `"?foo=bar"`), which means `getSegments()` returns an empty list `[]`
  - Create a base `Url` with no segments: `Url.parse("?foo=bar")` — this string has no path segments, only query parameters
  - Create a relative `Url` that is also query-only: `Url.parse("?a=b")`
  - Call `base.resolveRelative(relative)`
  - Verify the result: the base URL should end up equal to the relative URL (segments and query parameters replaced), e.g., `assertEquals("?a=b", base.toString())`
- WHEN the TG also tests with a relative URL that **has segments** being resolved against a base with **no segments**
  - Create base `Url.parse("?foo=bar")` (segments=[])
  - Create relative `Url.parse("bar/baz?a=b")` (segments=["bar","baz"])
  - Call `base.resolveRelative(relative)`
  - Verify the result equals `"bar/baz?a=b"` — the base's empty segments should be replaced entirely by the relative URL's segments
- **Common pitfall**: Only testing `resolveRelative` with base URLs that have segments (e.g., `"c/d"`, `"a/b"`), missing the boundary case of an empty segment list. The bug is that `segments.get(segments.size() - 1)` throws `ArrayIndexOutOfBoundsException` with failure message `"-1"` when `segments` is empty.
- **Correct test example**:
  ```java
  public void testResolveRelative_NoSegmentsInBase() {
      Url relative = Url.parse("?a=b");
      Url baseUrl = Url.parse("?foo=bar");
      baseUrl.resolveRelative(relative);
      assertEquals("?a=b", baseUrl.toString());
  }
  ```
- **Incorrect test example** (too narrow, misses the bug):
  ```java
  // Only tests cases where both base and relative have segments
  public void testResolveRelative_WithSegments() {
      Url relative = Url.parse("./a/b?p1=v1");
      Url baseUrl = Url.parse("c/d?p2=v2");
      baseUrl.resolveRelative(relative);
      assertEquals("c/a/b?p1=v1", baseUrl.toString());
  }
  ```