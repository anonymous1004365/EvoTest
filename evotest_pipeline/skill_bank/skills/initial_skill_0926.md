---
name: url-resolve-relative-dot-empty-segment
description: When resolving a relative URL against a base URL using Url.resolveRelative(),
  test that URL segments like "." followed by empty segments are correctly handled
  and do not produce unexpected trailing empty segments.
code_tags:
- URL_PARSING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# url-resolve-relative-dot-empty-segment

## Instructions

# URL resolveRelative Dot-Empty Segment Handling

## Instructions

- WHEN the TG encounters a `resolveRelative(Url relative)` method on `org.apache.wicket.request.Url` that resolves a relative URL path against a base URL path
- THEN the TG should test URL resolution where the relative URL contains a dot segment (".") followed by an empty segment (e.g., `"./"` as a trailing path)
  - Specifically, the TG should test a base URL like `Url.parse("protocol://host/path/path2")` and a relative URL like `Url.parse("./")`
  - Verify that after `base.resolveRelative(relative)`, the base URL does NOT end up with an unwanted trailing empty segment
  - The test should assert on `base.getSegments().size()` — on the buggy version, the size will be one more than expected (an extra empty string segment is appended)
  - Also test with `Url.parse(".")` as the relative URL, which should similarly not produce an extra empty segment
- Common pitfalls to avoid:
  - Testing only with non-empty relative URLs (e.g., `"foo/bar"`) and missing the edge case of `"./"` or `"."`
  - Asserting only on the string representation of the resolved URL (e.g., `toString()`) rather than the segments list size, since the extra empty segment may be invisible in string form
  - Not testing both `"./"` (dot followed by slash = dot followed by empty segment) and `"."` (just a dot)

Example of a correct test (what the TG should write):
```java
@Test
public void resolveRelative_DotFollowedByEmptySegment1() {
    Url baseUrl = Url.parse("protocol://host/path/path2");
    Url relative = Url.parse("./");
    baseUrl.resolveRelative(relative);
    assertEquals(2, baseUrl.getSegments().size());
}
```

Example of an incorrect test (too weak, would miss the bug):
```java
@Test
public void resolveRelative_TooWeak() {
    Url baseUrl = Url.parse("protocol://host/path/path2");
    Url relative = Url.parse("./");
    baseUrl.resolveRelative(relative);
    // This assertion would pass even with the bug
    assertEquals("protocol://host/path/path2", baseUrl.toString());
}
```