---
name: surrogate-character-json-encoding
description: When a JSON encoder handles surrogate characters (0xD800-0xDFFF), it
  must encode lone/unpaired surrogates as \\uXXXX escapes. Without proper encoding,
  surrogates get corrupted during UTF-8 round-tripping. Use this skill when validating
  encode/escape methods in JSON or Jsop builders.
code_tags:
- SURROGATE_CHARACTER_ENCODING
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# surrogate-character-json-encoding

## Instructions

# Surrogate Character JSON Encoding

## Instructions

- WHEN the TG encounters a `JsopBuilder.encode(String)` or `JsopBuilder.escape(String, StringBuilder)` method that processes JSON string encoding
- THEN it should create a test that passes a string containing a **lone (unpaired) high surrogate character** (e.g., `"\ud800"`) to the `JsopBuilder.encode(String)` method and verifies the output contains the proper `\ud800` escape sequence (the literal backslash-u-d-8-0-0 characters, not the decoded replacement character `?`)
- WHEN testing surrogate pairs (e.g., `"\ud83d\ude00"` for 😀), verify they are **NOT** escaped but preserved as-is in the output (since a valid surrogate pair round-trips correctly through UTF-8)
- WHEN testing lone low surrogates (e.g., `"\udc00"`), verify these are also properly escaped as `\udc00`

- **Common pitfalls to avoid:**
  - **Pitfall: Testing only valid surrogate pairs.** A valid UTF-16 surrogate pair (high + low) works fine, but the bug was specifically about lone/unpaired surrogates. Test both lone high surrogates AND lone low surrogates.
  - **Pitfall: Assuming non-printable or control characters are the only edge case.** The `encode()` method has a fast path: if no special characters are found, it skips escaping. The surrogate check must be done **before** the fast path branch. Verify the fast path (single-pass loop) correctly detects surrogates and falls through to the escape path.
  - **Pitfall: Testing only `encode()`, not the internal `escape()` method.** Both `encode()` and `escape()` need surrogate handling. Test `encode(String s)` which returns the full quoted JSON literal (e.g., `"\"\\ud800\""`) and also test that the character survives a round-trip through `JsopTokenizer.decode()`.

- **Correct example (Java):**
```java
public void testSurrogates() {
    // Buggy behavior: encode returns "?" (replacement char)
    // Fixed behavior: encode returns "\"\\ud800\""
    String s = JsopBuilder.encode("\ud800");
    assertEquals("\"\\ud800\"", s);

    // Valid surrogate pair should NOT be escaped
    String pair = JsopBuilder.encode("\ud83d\ude00");
    assertEquals("\"\ud83d\ude00\"", pair);

    // Lone low surrogate should be escaped
    String low = JsopBuilder.encode("\udc00");
    assertEquals("\"\\udc00\"", low);
}
```

- **Incorrect example that would miss the bug:**
```java
public void testSurrogates() {
    // Only testing valid surrogate pair — passes on both buggy and fixed
    String s = JsopBuilder.encode("\ud83d\ude00");
    assertEquals("\"\ud83d\ude00\"", s);
    // ❌ Does NOT detect the bug because valid pairs are handled correctly
    // ❌ Must test lone "\ud800" to catch the broken encoding
}
```