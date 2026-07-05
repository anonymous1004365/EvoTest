---
name: alternative-protocol-decoding-path-validation
description: When a protocol decoder has an alternative/fallback decoding path that handles non-standard messages, tests must exercise that alternative path with various malformed or partial payloads to catch validation gaps. This skill teaches how to construct inputs that force the alternative decoder branch and verify it handles edge cases correctly.
code_tags: ['VALIDATION', 'ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path-validation

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol frame decoder that has an alternative decoding path (e.g., an `else` branch, fallback decoder, or secondary `decode` logic that handles non-standard frame formats)
- THEN the TG should write tests that explicitly force execution through the alternative decoding path by providing inputs that fail the primary decoding logic (e.g., malformed headers, unexpected length fields, missing fields)
- Include test cases for the alternative path with:
  - Partial/broken payloads that have valid framing but invalid content for the primary decoder
  - Unexpected field types or values in fields the alternative path parses
  - Boundary values for fields used in the alternative path logic (e.g., zero-length, maximum-length fields)
  - Null or absent optional fields that the alternative path might access
- Verify that the alternative decoding path handles each input correctly (produces a properly decoded result or an appropriate exception) rather than crashing with a NullPointerException, ArrayIndexOutOfBoundsException, or silently returning null/malformed data
- Common pitfalls to avoid:
  - Testing only the "happy path" where the primary decoder handles the message
  - Assuming the alternative path has the same validation rigor as the primary path
  - Not testing with fields that have unexpected types (e.g., providing an integer where a string is expected in the alternative path)
  - Not testing with malformed length fields that could cause buffer over-reads in the alternative path

### Correct Example (parametric test covering alternative path)
```java
@Test
public void testDecodeAlternativePathWithPartialPayload() {
    StarLinkProtocolDecoder decoder = new StarLinkProtocolDecoder(...);
    
    // Payload that passes framing but triggers alternative decode branch
    // e.g., header indicates alternative format, body is truncated
    byte[] partialPayload = {0x01, 0x02, (byte)0xFF, 0x00, 0x0A};
    
    assertThrows(IllegalArgumentException.class, () -> {
        decoder.decode(channel, remoteAddress, partialPayload);
    });
}

@ParameterizedTest
@ValueSource(strings = {
    "invalid_field_type",
    "",                          // empty
    "A".repeat(256)             // very long field value
})
public void testDecodeAlternativePathEdgeCases(String fieldValue) {
    // Test with various field values that the alternative path must handle
}
```

### Incorrect Example (missing alternative path coverage)
```java
// WRONG: Only tests the standard/primary decoding path
@Test
public void testDecodeStandardMessage() {
    StarLinkProtocolDecoder decoder = new StarLinkProtocolDecoder(...);
    byte[] validPayload = {/* standard format */};
    Object result = decoder.decode(channel, remoteAddress, validPayload);
    assertNotNull(result);
    // Never exercises the alternative/fallback decoding branch
}
```