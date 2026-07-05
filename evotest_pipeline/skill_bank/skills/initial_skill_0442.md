---
name: json-parse-invalid-token-handling
description: When parsing JSON/Jsop with multi-line or escaped unicode characters,
  test that the parser does not crash on special control characters like \u0001. This
  skill helps prevent tokenizer failures during document deserialization.
code_tags:
- VALIDATION
- STATE_MUTATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# json-parse-invalid-token-handling

## Instructions

# JSON Parser Invalid Token Handling

## Instructions

WHEN the TG encounters a JSON or Jsop parser that reads and tokenizes character data (especially in a `DocumentMK`, `DocumentPropertyState`, or `RDBDocumentSerializer` context):

- THEN the TG should test that the parser correctly handles / rejects special control characters (e.g., `\u0001`, `\u0000`, `\u001f`) inside quoted strings or multi-line values.
- THEN the test should supply a JSON/Jsop input containing a single control character (e.g., `"\u0001"`) and verify that the parse does not throw an opaque `DocumentStoreException("token: ...")` or that it throws an appropriate parse/illegal argument exception instead of a cryptic token error.
- THEN the test should also supply a JSON/Jsop input containing multiple escaped control characters (e.g., `"line1\u0001\nline2"`) and confirm the parser either escapes them properly, rejects them with a clear message, or processes them without corrupting subsequent tokens.
- THEN include a negative test: provide a malformed or truncated token (e.g., unclosed string `"abc`) and assert that the parser throws a clear parse exception rather than getting stuck or producing an invalid internal state.

Common pitfalls to avoid:
- Testing only valid/well-formed JSON inputs — the TG might miss the need for edge-case character inputs.
- Assuming the parser handles all unicode characters safely — some parsers use token types that map directly to raw characters and fail on control characters.
- Forgetting to test multi-line or concatenated values — the bug manifests when combining `text + jsonString` (e.g., `${text}${jsonString}`) where the text contains a character whose token type is an internal control code.

### Example: Correct test approach (fails on buggy, passes on fixed)

```
@Test
public void testParseSpecialControlChar() {
    String input = "\"\\u0001\"";
    try {
        JsonObject result = Json.parse(input);
        assertEquals("\u0001", result.asString());
    } catch (DocumentStoreException e) {
        fail("Parser should not throw cryptic token error on \\u0001: " + e.getMessage());
    }
}
```

### Example: Incorrect test approach (won't catch the bug)

```
@Test
public void testParseSimpleString() {
    String input = "\"hello\"";
    JsonObject result = Json.parse(input);
    assertEquals("hello", result.asString());
    // Only tests basic case — does not expose the control-character crash
}
```