---
name: obd-dongle-alternative-format-decoding
description: When a protocol decoder has an alternative decoding path (e.g. trying
  different message formats), test that each path properly validates the message format
  and throws an exception on malformed data rather than returning null or silently
  failing.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: EXCEPTION_TEST
---

# obd-dongle-alternative-format-decoding

## Instructions

# OBD Dongle Alternative Format Decoding

## Instructions

- WHEN the TG encounters a protocol frame decoder that supports multiple message formats or has an alternative decoding path (e.g., `ObdDongleProtocolDecoder` trying different message types or formats)
- THEN the TG should write a test that sends malformed/incorrectly formatted messages in the alternative format path and verify that the decoder throws an appropriate exception (e.g., `IllegalArgumentException`, `IndexOutOfBoundsException`, or `RuntimeException`) rather than returning null or silently failing
- Include concrete test inputs: use the exact channel buffer format expected by the decoder, but with an invalid or unrecognizable message type/format that would exercise the alternative path
- Common pitfalls: testing only the primary/expected message format; not testing the alternative decoding branch; asserting that the decoder returns a result (non-null) when it should throw; not providing the exact byte-level input format that exercises the alternative path
- The test should ideally verify that on the buggy version, the alternative path either throws an exception or crashes with a clear error, while on the fixed version it handles the malformed input gracefully

### Correct Example
```java
@Test
public void testDecodeWithInvalidAlternativeFormat() {
    ChannelBuffer buf = ChannelBuffers.copiedBuffer(
        "invalid_format_data_that_triggers_alternative_path", 
        CharsetUtil.US_ASCII
    );
    // Verify that decoding throws an exception instead of returning null/empty
    assertThrows(Exception.class, () -> decoder.decode(buf));
}
```

### Incorrect Example (what to avoid)
```java
@Test
public void testDecodeBasicFormat() {
    ChannelBuffer buf = ChannelBuffers.copiedBuffer("valid_format_data", CharsetUtil.US_ASCII);
    // Only tests the primary path; misses the alternative decoding branch
    Object result = decoder.decode(buf);
    assertNotNull(result);
}
```