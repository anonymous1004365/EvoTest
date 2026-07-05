---
name: link-parser-markup-avoidance
description: This skill teaches how to test parsers that should avoid processing content
  that already contains HTML markup. When a link parser detects '<' in the input,
  it should skip link replacement entirely and return the text unchanged.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# link-parser-markup-avoidance

## Instructions

# Link Parser Markup Avoidance

## Instructions

- WHEN the TG encounters a `LinkParser` (or similar text parser) that uses a guard condition like `if (work.indexOf('<') == -1)` to skip processing when HTML markup is detected,
- THEN the TG should write a test that calls `parser.parse(text)` with input text that already contains HTML anchor elements (e.g., `<a href="http://some.url">label</a>`) and verify that:
  1. The returned String equals the original input text exactly — no transformation should occur.
  2. The method `parse(String)` returns the unchanged input, not a re-parsed or doubly-wrapped link (e.g., avoid the bug where `<a href="http://some.url">label</a>` becomes `<a href="<a href="http://some.url">http://some.url</a>">label</a>`).
  3. Test with inputs that contain `<` anywhere in the text (not just anchor tags), since the guard checks for any `<` character.
- Common pitfalls:
  - Testing only plain text inputs (no HTML) — this will pass on buggy code but miss the regression.
  - Testing only email or URL patterns without markup — these do not trigger the `<` guard.
  - Assuming the parser "intelligently" detects only non-link HTML — the guard is a simple character check for `'<'`.
  - Using `assertEquals` with expected values that contain re-parsed/transformed HTML — the correct expectation is the **unchanged original input**.

### Correct Example (catches the bug)
```java
@Test
public void dontParseMarkup()
{
    String text = "<a href=\"http://some.url\">label</a>";
    ILinkParser parser = new DefaultLinkParser();
    String parsed = parser.parse(text);
    assertEquals(text, parsed);  // Bug: returns "<a href=\"<a href=\"http://some.url\">http://some.url</a>\">label</a>"
}
```

### Incorrect Example (misses the bug)
```java
@Test
public void testUrlParsing()
{
    ILinkParser parser = new DefaultLinkParser();
    // Only tests plain text URLs — these pass even on buggy code
    assertEquals("<a href=\"http://www.test.com\">http://www.test.com</a>",
        parser.parse("http://www.test.com"));
}
```