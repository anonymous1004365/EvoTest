---
name: email-pattern-hyphen-minus-in-character-class
description: When building a regex pattern for email addresses where the hyphen-minus
  character (`-`) should be part of the local part, ensure the hyphen is either placed
  at the start/end of the character class or escaped (`\-`). A misplaced hyphen inside
  a character class creates an unintended range (e.g., `[\\w\\.\\-\\\\+]` is correct
  but `[\\w\\.\\-\\\\+\\-]` may break). Test with email addresses containing hyphens
  like `my-test@example.com`.
code_tags:
- REGEX_PATTERN_CHARACTER_MISMATCH
test_pattern: PARAMETRIC_TEST
---

# email-pattern-hyphen-minus-in-character-class

## Instructions

# Email Regex Pattern: Hyphen-Minus in Character Class

## Instructions

- WHEN the TG encounters a regex pattern for email addresses (e.g., a `String emailPattern` or similar local-part regex containing a character class `[...]`) that is intended to match the local part of an email address (the part before the `@`)
- THEN the TG MUST specifically test for the **hyphen-minus character (`-`)** being correctly matched as part of the local part, using inputs such as `"my-test@example.com"` and verifying that the full email address (including the hyphen) is captured as a single match
- The TG should also test the `+` character in email local parts (e.g., `"my+test@example.com"`) to confirm it too is included, since both characters must be legal per RFC 5322 and the pattern `[\\w\\.\\-\\\\+]+` or equivalent
- WHEN the regex pattern contains a character class with `\-`, verify that the hyphen-minus is NOT creating an unintended range. If the hyphen appears in the middle of the class without proper escaping or position, it may be interpreted as a range operator (e.g., `[a-z]` means range `a` to `z`, while `[a\-z]` escapes the hyphen). The pattern `[\\w\\.\\-\\\\+]` is correct because the `\-` is an escaped hyphen; however, a misplaced raw hyphen (e.g., `[\\w.-\\+]`) would make `.-\\` an unintended range.
- THEN use `DefaultLinkParser` (or the relevant parser class) to `parse()` the input and assert the output equals the expected `<a href="mailto:...">...</a>` link, specifically checking that **all characters** (including hyphen and plus) appear in both the `href` value and the link text
- Common pitfalls to avoid:
  - Testing only `"test@example.com"` (no special chars) — this passes even if hyphen/plus are broken
  - Testing only `"my+test@example.com"` — this passes on buggy code that already handled `+` but not `-`
  - Assuming that because `\-` is an escape sequence, the pattern definitely works — the position of the raw hyphen in a character class still matters (e.g., `[\\w.-]` is ambiguous)
  - Not asserting the **full expected string**, only checking that the output contains email-like content
  - Using `assertTrue(result.contains(...))` instead of `assertEquals(expected, result)` — partial assertions can hide bugs where only part of the address is captured

**Correct example (catches the bug):**
```java
@Test
public void testEmailWithMinusChar()
{
    final String testEmailAddress = "my-test@example.com";
    final String testExpectedLink = "<a href=\"mailto:my-test@example.com\">my-test@example.com</a>";

    ILinkParser parser = new DefaultLinkParser();
    final String result = parser.parse(testEmailAddress);
    assertEquals("Expected chars to left of - to be included in the link.", testExpectedLink, result);
}
```

**Incorrect example (does NOT catch the bug):**
```java
@Test
public void testEmailWithMinusChar()
{
    final String testEmailAddress = "my-test@example.com";
    ILinkParser parser = new DefaultLinkParser();
    final String result = parser.parse(testEmailAddress);
    assertTrue("Should contain href", result.contains("mailto:"));
    // BUG: This assertion passes even when only "test@example.com" is captured,
    // because "mailto:" is still present. The hyphen and "my-" are silently dropped.
}
```