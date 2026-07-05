---
name: protocol-decoder-alternative-path-testing
description: When a protocol decoder has multiple decoding paths (e.g., primary and
  fallback), test both paths with valid and malformed input to ensure they handle
  protocol data correctly. This skill helps prevent silent failures where the decoder
  fails on an alternative path but incorrectly returns a partial or default result.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- VALIDATION
- EXCEPTION_HANDLING
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-alternative-path-testing

## Instructions

# Protocol Decoder Alternative Path Testing

## Instructions

- WHEN testing a protocol decoder that has an alternative/fallback decoding path (e.g., a `try-catch` that falls back to a different parsing strategy, or an `if-else` branch that handles edge cases differently)
- THEN the TG should write parametric tests that feed specific protocol data through BOTH paths:
  - Test the primary (happy-path) decoding path with well-formed protocol messages
  - Test the alternative/fallback path with messages that trigger the fallback condition (e.g., missing fields, wrong field types, corrupted prefixes, empty payloads)
  - Verify the decoder produces the correct output (e.g., parsed position, device ID, timestamp) for each path
  - Explicitly assert that no exception escapes the decoder — the decoder must handle all parse failures gracefully without throwing

- Common pitfalls to avoid:
  - Testing only the primary decoding path and assuming the alternative path works identically
  - Forgetting that field type mismatches (e.g., passing an `Object` where a `String` is expected) can silently cause the alternative path to produce wrong results instead of throwing
  - Not testing with zero-length or partially-filled protocol frames that trigger the fallback
  - Assuming that if no exception is thrown, the output is correct — always assert specific field values

- Correct approach example:
```java
// Test primary path
@Test
public void testDecodePrimaryPath() {
    ProtocolDecoder decoder = new MyProtocolDecoder();
    String msg = "valid-protocol-message-with-all-fields";
    Position position = decoder.decode(msg);
    assertNotNull(position);
    assertEquals(expectedLat, position.getLatitude(), 0.001);
}

// Test alternative path with messed-up field type (triggers fallback)
@Test
public void testDecodeAlternativePath() {
    ProtocolDecoder decoder = new MyProtocolDecoder();
    String msg = "protocol-with-numeric-field-where-string-expected";
    Position position = decoder.decode(msg);
    assertNotNull(position); // fallback must produce a result
    // Verify fallback logic is correct
}
```

- Incorrect approach (testing only the happy path):
```java
// BAD: Only tests the primary path
@Test
public void testDecode() {
    ProtocolDecoder decoder = new MyProtocolDecoder();
    String msg = "perfect-protocol-message";
    Position position = decoder.decode(msg);
    assertNotNull(position);
    // Missing: tests for fallback path, missing fields, wrong types
}
```