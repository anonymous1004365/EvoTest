---
name: surrogate-character-encoding
description: When encoding or escaping JSON strings that may contain surrogate pairs
  (Unicode characters outside the BMP), test that both high and low surrogates in
  a surrogate pair are correctly preserved. Without proper handling, lone surrogates
  or broken pairs can be silently corrupted or replaced with '?'.
code_tags:
- STRING_PARSING
- VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# surrogate-character-encoding

## Instructions

# Surrogate Character Encoding in JSON/String Escaping

## Instructions

- WHEN the TG encounters a method that encodes, escapes, or tokenizes JSON strings — especially methods that handle Unicode escape sequences (e.g., `\uXXXX`) or produce valid JSON output — THEN the TG should include a test case that verifies correct handling of surrogate characters (Unicode code points U+D800–U+DFFF).

- WHEN testing surrogate handling, THEN the TG should test with **both**:
  1. A valid surrogate **pair** (e.g., a high surrogate `\uD800` followed by a low surrogate `\uDC00`) — these should be preserved as-is in the escaped output.
  2. A **broken/lone surrogate** (e.g., a high surrogate `\uD800` without a following low surrogate) — this character must NOT be silently dropped, replaced with `?`, or otherwise corrupted. The raw surrogate code point should be preserved in the output.

- WHEN the method under test performs JSON escaping (wrapping strings in quotes, escaping special characters), THEN the TG should verify that surrogate code points that are NOT part of a valid pair are output as the raw `\uXXXX` escape sequence rather than being replaced or lost.

- WHEN the TG tests encoding of strings containing surrogate characters, THEN the TG should:
  - Use concrete hardcoded expected output strings (e.g., `"\"surrogate-broken: \\ud800 \""`) to verify exact character-level preservation.
  - Avoid testing only "nice" Unicode characters (e.g., ASCII, Latin-1, or even CJK). The edge case is specifically the surrogate range (U+D800–U+DFFF).

- Common pitfalls to avoid:
  - ❌ Testing only with BMP characters (U+0000–U+FFFF outside the surrogate range).
  - ❌ Assuming that `StringEscapeUtils.escapeJson()` or similar standard JSON escaping handles surrogates correctly — libraries vary.
  - ❌ Writing tests that only check for the absence of exceptions, rather than asserting exact output.
  - ❌ Using `assertEquals(String, String)` with loose comparison that could hide surrogate corruption (e.g., using `contains()` instead of exact match).

### Correct Example (catching the surrogate-broken bug):
```java
@Test
public void testSurrogates() {
    // Test valid surrogate pair
    assertEquals("\"surrogate-pair: \\ud800\\udc00\"", 
        JsopBuilder.encode("surrogate-pair: \ud800\udc00"));
    
    // Test broken/lone surrogate (high surrogate without low surrogate)
    assertEquals("\"surrogate-broken: \\ud800 \"", 
        JsopBuilder.encode("surrogate-broken: \ud800 "));
    
    // Test lone low surrogate
    assertEquals("\"surrogate-lone-low: \\udc00 \"", 
        JsopBuilder.encode("surrogate-lone-low: \udc00 "));
}
```

### Incorrect Example (missing the surrogate edge case):
```java
@Test
public void testEncode() {
    // Only tests ordinary characters — MISSING surrogate edge case
    assertEquals("\"hello\"", JsopBuilder.encode("hello"));
    assertEquals("\"tab:\\t\"", JsopBuilder.encode("tab:\t"));
    // Broken surrogates silently replaced with '?' — test passes when it shouldn't
    assertEquals("\"surrogate-broken: ? \"", JsopBuilder.encode("surrogate-broken: \ud800 "));
}
```