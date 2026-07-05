---
name: email-regex-with-special-chars
description: When testing email link parsing in DefaultLinkParser, the email regex
  pattern includes escaped special characters like `\\+` that can behave unexpectedly.
  This skill teaches how to test regex patterns that contain escaped special characters
  within larger character classes.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- EDGE_CASE_INPUT
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# email-regex-with-special-chars

## Instructions

# Email Regex Pattern with Escaped Special Characters

## Instructions

- WHEN the TG encounters a `DefaultLinkParser` that defines an email regex pattern using `[\\w\\.\\-\\\\+]+` (or similar patterns with escaped special characters in a character class) to match email addresses in text
- THEN the TG should create a parameterized test that:
  - Tests email addresses containing the special character that is escaped in the regex (e.g., the `+` character since the pattern includes `\\+`)
  - Tests that the email address "user+tag@example.com" is correctly parsed into an `EmailLink` (not an `HttpLink`)
  - Verifies that the link's URL is "mailto:user+tag@example.com" (preserving the `+`)
  - Tests the `buildLink` method by constructing a `LinkParser.Scope` with `LinkParser.LinkState` containing the matched email text and checking the resulting `ILink` type
  - Avoids the mistake of only testing email addresses without special characters like `+`, which would pass on the buggy code
  - Avoids the mistake of trusting the documentation/comments without testing the actual regex behavior

- **Common pitfalls**:
  - Testing only standard email patterns like "user@example.com" or "first.last@example.com"
  - Assuming that `\\+` in a Java regex character class correctly matches the `+` literal (in this bug, the backslash is consumed by Java string escaping, so `\\+` becomes `\+` inside the character class, but `+` is already treated as a literal inside `[]`, so the regex is redundant but should still work — however the actual bug shows it fails)
  - Not testing edge characters that appear inside the character class like `+`, `\`, or `.`

- **Example of correct test** (should detect the bug):
  ```java
  @Test
  void testEmailWithPlusChar()
  {
    DefaultLinkParser parser = new DefaultLinkParser();
    String text = "user+tag@example.com";
    ILinkParser.ILink[] links = parser.parse(text);
    assertNotNull(links, "Expected a link to be found");
    assertEquals(1, links.length, "Expected exactly one link");
    assertTrue(links[0] instanceof DefaultLinkParser.EmailLink, 
        "Expected an EmailLink for 'user+tag@example.com', but got: " + links[0].getClass().getSimpleName());
  }
  ```

- **Example of insufficient test** (would miss the bug):
  ```java
  @Test
  void testEmailWithoutSpecialChars()
  {
    DefaultLinkParser parser = new DefaultLinkParser();
    ILinkParser.ILink[] links = parser.parse("user@example.com");
    assertEquals(1, links.length);
    // This test passes even on buggy code, giving false confidence
  }
  ```