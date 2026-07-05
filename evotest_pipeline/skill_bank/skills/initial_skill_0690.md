---
name: full-mode-url-segment-validation
description: When rendering a URL in FULL mode, segments containing ".." must be rejected
  with an IllegalStateException. This skill teaches the TG to test URL toString methods
  with StringMode.FULL for all segment patterns that contain two consecutive dots.
code_tags:
- URL_STRINGMODE_SEGMENT_VALIDATION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# full-mode-url-segment-validation

## Instructions

# Full Mode URL Segment Validation

## Instructions

- WHEN the TG encounters a `Url.toString(StringMode, Charset)` method or any URL rendering that converts URL segments to a string using `StringMode.FULL`, specifically checking segment content for `".."`,
- THEN the TG should test with URL segments that contain two consecutive dots (`".."`) in various positions (as a standalone segment, as part of a longer segment like `"whatever..."`), and verify that calling `toString(StringMode.FULL, charset)` throws an `IllegalStateException` with a message indicating the `".."` segment cannot be rendered in FULL mode.
  - Use specific examples: a segment `".."` and a segment `"whatever..."` should both trigger the exception.
  - Verify the exception message contains the rendered URL fragments.
  - The fix should accept valid segments with single dots (`.`) or segments without dots.
- WHEN testing URL segment validation, common pitfalls to avoid include:
  - Testing only the `".."` standalone segment but missing segments that end with `"..."` (three dots, which contains two consecutive dots).
  - Testing only `StringMode.LOCAL` but not `StringMode.FULL`.
  - Not catching the `IllegalStateException` and instead expecting a normal return value.

### Example (correct test)

```java
@Test
public void wicket_5114_allowtoStringFullWhenContainingTwoDots()
{
    Url url = Url.parse("/mountPoint/whatever.../");
    try
    {
        url.toString(StringMode.FULL, charset);
        Assert.fail("Expected IllegalStateException because the URL has a '..' segment");
    }
    catch (IllegalStateException e)
    {
        Assert.assertTrue(e.getMessage().contains("Cannot render this url in FULL mode " +
            "because it has a `..` segment"));
    }
}
```

### Example (incorrect test — missing the case)

```java
// Wrong: only tests LOCAL mode, not FULL mode
@Test
public void testUrlWithTwoDots() {
    Url url = Url.parse("/a/../b");
    String result = url.toString(StringMode.LOCAL, charset);
    Assert.assertNotNull(result); // This passes but doesn't verify FULL mode behavior
}
```