---
name: unicode-escape-decoding
description: When parsing JSON-like tokens that contain Unicode escape sequences (e.g.,
  \u0123), test that the decoder properly converts them to actual Unicode characters
  rather than leaving them as escaped strings. Use this skill whenever working with
  string tokenization and unescaping logic.
code_tags:
- UNICODE_ESCAPE_DECODING
test_pattern: PARAMETRIC_TEST
---

# unicode-escape-decoding

## Instructions

# Unicode Escape Decoding in Tokenizers

## Instructions

- WHEN the TG encounters a tokenizer or decoder that processes JSON-like strings containing Unicode escape sequences (e.g., `\u0123`, `\u0041`)
- THEN it should write a test that:
  1. Passes a string literal containing a `\uXXXX` escape sequence (e.g., `"\u0123"` which is the character `ģ`) into the tokenizer/decoder
  2. Reads back the decoded token via the appropriate getter method (e.g., `getToken()` or `readString()`)
  3. Asserts that the returned value is the actual Unicode character, NOT the escaped representation (e.g., assert that `getToken()` returns `"ģ"`, not `"\\u0123"`)
  4. For the specific JsopTokenizer case: after calling `read('"')` to consume the opening quote, read the string with `reader.getToken()` and compare against the expected decoded character

- Common pitfalls to avoid:
  - **Testing only ASCII or plain strings**: Ensure at least one test uses a non-ASCII Unicode escape (code point above U+007F) like `\u0123` (ģ) or `\u00E9` (é)
  - **Comparing against the escaped form**: The test must compare against `"ģ"` (the actual character), not `"\\u0123"` (the escape sequence)
  - **Forgetting to trigger the decoding path**: Some tokenizers only decode when they detect escape sequences — make sure the input uses `\uXXXX` notation so the decode branch is exercised

### Correct Example (catching the bug)

```java
// JsopTokenizer correctly decodes Unicode escape \u0123 to character ģ
@Test
public void testUnicodeDecode() {
    JsopTokenizer tokenizer = new JsopTokenizer("\"\\u0123\"");
    assertEquals('"', tokenizer.read('"'));
    assertEquals("ģ", tokenizer.getToken());
}
```

This test would fail on the buggy version (returning `"\\u0123"` instead of `"ģ"`) and pass on the fixed version.

### Incorrect Example (missing the bug)

```java
// WRONG: Only tests ASCII escapes, missing the Unicode decoding bug
@Test
public void testSimpleEscape() {
    JsopTokenizer tokenizer = new JsopTokenizer("\"\\n\"");
    assertEquals('"', tokenizer.read('"'));
    assertEquals("\n", tokenizer.getToken());
}
```

This test only exercises simple escapes like `\n` which were already handled, and never triggers the Unicode `\uXXXX` decoding path that contained the bug.