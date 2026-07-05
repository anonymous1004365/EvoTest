---
name: alternative-protocol-decoder-path
description: When a protocol decoder has a primary parsing path and an alternative
  fallback path, the TG should test both paths to ensure the alternative path doesn't
  throw unexpected exceptions (e.g., StringIndexOutOfBoundsException) due to unvalidated
  assumptions about input format.
code_tags:
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# alternative-protocol-decoder-path

## Instructions

# Alternative Protocol Decoder Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `IdplProtocolDecoder`) that decodes device messages by attempting a primary parsing approach (e.g., using a regex pattern like `Pattern.compile("...")`) and has a fallback/alternative path (e.g., a `try-catch` block that catches `PatternSyntaxException` and uses a different parsing method like `String.indexOf`/`String.substring` on the raw input)
- THEN the TG should write a test that exercises the **alternative/fallback decoding path** with input that would cause the primary approach to fail but is still valid input for the alternative path
- The test must verify that the alternative path does **not** throw an uncaught `StringIndexOutOfBoundsException`, `IndexOutOfBoundsException`, or any other unexpected runtime exception

### Common pitfalls to avoid:
- ❌ Only testing the primary/successful decoding path (the "happy path")
- ❌ Assuming that because the primary path handles a certain format, the alternative path handles the same format identically
- ❌ Not testing with input that triggers the `catch` block of a `try-catch` in the decoder
- ❌ Providing only well-formed, expected input that always succeeds on the primary path

### Correct test approach:
```java
// Test the alternative path by providing input that fails primary parsing
// (e.g., a message format that doesn't match the primary regex pattern
//  but is still valid for the alternative String-based parsing)
@Test
public void testDecodeAlternativePath() throws Exception {
    IdplProtocolDecoder decoder = new IdplProtocolDecoder(new Protocol("idpl"));
    
    // Input that triggers the regex failure and enters the catch/alternative block
    // For example, a message with unexpected format that the alternative path
    // tries to parse via String methods
    String altInput = "some format that won't match primary regex";
    
    // Should NOT throw StringIndexOutOfBoundsException
    assertDoesNotThrow(() -> decoder.decode(null, null, altInput));
}
```

### Incorrect test approach:
```java
// ❌ Only tests the happy path with well-formed input
@Test
public void testDecode() throws Exception {
    IdplProtocolDecoder decoder = new IdplProtocolDecoder(new Protocol("idpl"));
    // Only tests input that matches the primary path
    String input = "2024-01-01T00:00:00+00:00,id:123,fix:valid";
    Object result = decoder.decode(null, null, input);
    assertNotNull(result);
}
```