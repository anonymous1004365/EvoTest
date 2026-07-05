---
name: javascript-stripper-comment-downlevel-mode
description: Tests for JavaScript comment stripper that must not strip //-style line
  comments occurring inside string literals, especially when running in "downlevel"
  mode where partial HTML-like tags (<) inside scripts trigger state transitions.
  Use this skill when testing JS minification or comment removal logic.
code_tags:
- JAVASCRIPT_STRIPPING_COMMENT_HANDLING
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# javascript-stripper-comment-downlevel-mode

## Instructions

# JavaScript Stripper Comment Handling in Downlevel Mode

## Instructions

- WHEN the TG encounters a `JavascriptStripper` class that removes JavaScript comments (both multi-line `/* */` and single-line `//`) from inline script content, AND there is a state machine tracking `SCRIPT`, `COMMENT`, `STRING`, or similar modes,
- THEN the TG should test that `//` line comments appearing **inside** JavaScript string literals (`'...'` or `"..."`) are NOT stripped. The stripping should only apply to `//` comments at the top level of JavaScript code, not those that happen to be part of a string value like `"some//text"` or `'some//text'`.
- Specifically, WHEN the state machine has a "downlevel" mode (a fallback/compatibility mode) where the stripper treats `<` inside script content as potentially opening a downlevel-hidden block (e.g., treating `<!--` or `<` as hiding content for older browsers), THEN the TG should verify that:
  1. A string literal containing `//` is preserved verbatim (no character removed).
  2. A string literal containing `<` (e.g., `"<"`) does NOT cause the stripper to enter a downlevel/hidden state.
  3. Real `//` comments at the JavaScript top level ARE still stripped correctly.
- Common pitfalls:
  - Testing only the normal script stripping path and not the downlevel path.
  - Failing to use string literals that contain both `<` (triggers downlevel mode) and `//` (triggers comment detection) simultaneously.
  - Assuming that comment stripping is purely text-based without understanding the state machine transitions (e.g., inside a string, `<` should NOT trigger downlevel, and `//` should NOT trigger comment removal).

### Correct Example (what TG SHOULD write)

```java
@Test
void testCommentInStringLiteralInDownlevelMode() {
    // This input has assignString = "//" inside a script that also uses < downlevel markers
    String input = "<script>var x = \"//\";</script>";
    String expected = "<script>var x = \"//\";</script>";

    // Simulate downlevel mode (strip <...> but keep x = "//" intact)
    String actual = JavascriptStripper.stripCommentsAndDownlevelMarkers(input);
    assertEquals(expected, actual);
}
```

### Incorrect Example (what TG should AVOID)

```java
@Test
void testCommentStripping() {
    // BUG: This test does NOT trigger the buggy downlevel path.
    // It only tests normal comment stripping (no < character present),
    // so it passes even on the buggy version.
    String input = "var x = \"//\";";
    String expected = "var x = \"//\";";
    String actual = JavascriptStripper.stripCommentsAndDownlevelMarkers(input);
    assertEquals(expected, actual);
}
```