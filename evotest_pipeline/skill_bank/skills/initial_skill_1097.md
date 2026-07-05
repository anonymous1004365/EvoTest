---
name: url-path-compact-segments
description: When testing URL path manipulation that involves ".." segments, test
  that compact() correctly removes ".." and its preceding segment. The bug was that
  Url.compact() failed when a ".." segment followed by another segment "d" was not
  properly resolved — "b/../d" should become "d", not remain as "b/../d".
code_tags:
- URL_COMPACT_SEGMENTS
test_pattern: STATE_TEST
---

# url-path-compact-segments

## Instructions

# URL Path Compact Segments

## Instructions

- WHEN the code contains a method named `compact()` on a URL or path class that is intended to resolve ".." (parent directory) segments in a list of path segments
- THEN the TG should write tests that verify the compact method correctly resolves ".." segments by removing both the ".." segment and the segment immediately before it
  - Test with segments like `["a", "b", "..", "d"]` and verify the result is `["a", "d"]`
  - Test with a ".." at the beginning: `["..", "a"]` and verify ".." is preserved (cannot go above root)
  - Test with consecutive ".." segments like `["a", "b", "..", "..", "c"]` and verify the result is `["c"]`
  - Test with an empty string segment followed by "..": `["", "a", ".."]` should compact to `[""]`
  - Use `Url.parse(urlString)` to create the URL, then call `.compact()` on the returned `Url` object, then check `.getSegments()` 
  - The expected behavior is that `compact()` modifies the list of segments **in place** — check the segments list after calling `compact()`
- The test should verify that segments like `["a", "b", "..", "d"]` produce `["a", "d"]` after compaction — this is the specific case that triggered the bug (failure message: `expected:<a/[]d> but was:<a/[b/../]d>`)
- Avoid these common mistakes:
  - ❌ Testing only single-level ".." resolution (e.g., `["a", ".."]` → `[]`) without testing ".." followed by a normal segment
  - ❌ Forgetting to check that ".." at the beginning of the path is left untouched
  - ❌ Only testing with a single ".." without testing chains of multiple ".." segments
  - ❌ Assuming `compact()` returns a new Url instead of modifying the existing one in place

### Correct Example

```java
@Test
public void compact()
{
    // Bug case: ".." followed by a normal segment "d" should be compacted
    Url url = Url.parse("a/b/../d");
    url.compact();
    checkSegments(url, "a", "d");

    // Additional cases
    url = Url.parse("a/b/../c/../d");
    url.compact();
    checkSegments(url, "a", "d");

    // ".." at beginning should be preserved
    url = Url.parse("../a");
    url.compact();
    checkSegments(url, "..", "a");
}
```

### Incorrect Example

```java
@Test
public void compact()
{
    // ❌ Only testing simple case — does not catch the "b/../d" bug
    Url url = new Url();
    url.getSegments().add("a");
    url.getSegments().add("..");
    url.compact();
    checkSegments(url);  // passes but doesn't test the failing case

    // ❌ Missing the case where ".." is followed by a real segment
}
```