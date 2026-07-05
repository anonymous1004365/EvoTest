---
name: protocol-decoder-message-parsing-exception
description: When writing tests for protocol decoders that parse position data, test
  with varying lengths of hex messages including truncated/incomplete messages to
  verify proper exception handling. The TG should understand that protocol decoders
  must gracefully handle invalid or incomplete hex message formats.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# protocol-decoder-message-parsing-exception

## Instructions

# Protocol Decoder Message Parsing Exception Handling

## Instructions

- WHEN the TG is testing a protocol decoder (e.g., `HomtecsProtocolDecoder`) that parses hex-encoded position messages from a `ChannelBuffer`
- THEN the TG should include test cases that verify proper exception handling for malformed, truncated, or invalid input data
- WHEN the decoder parses position data using methods like `parsePositionData` with a hex string buffer
- THEN the TG should test with:
  1. **Truncated messages** — hex strings with missing fields or incomplete segments
  2. **Invalid hex characters** — non-hexadecimal characters in the message
  3. **Empty or null buffers** — empty `ChannelBuffer` or null input
  4. **Messages with wrong field types** — where a numeric field contains non-numeric data
- The test should verify that `IndexOutOfBoundsException` or similar runtime exceptions are properly handled and don't propagate as uncaught exceptions
- Common pitfalls:
  - Testing only with well-formed, complete messages (happy path only)
  - Not testing with buffers at various readable byte lengths (boundary conditions)
  - Assuming all hex messages will have the same structure/field count
- Expected behavior on buggy version: the decoder throws an uncaught `IndexOutOfBoundsException` or similar when processing incomplete/malformed messages
- The test should catch the specific exception type that gets thrown and verify the device session/connection is properly cleaned up

### Correct Example:
```java
// Test with truncated message — missing fields
@Test
public void testDecodeWithTruncatedMessage() {
    HomtecsProtocolDecoder decoder = new HomtecsProtocolDecoder(new HomtecsProtocol());
    // Provide a hex message with insufficient bytes
    byte[] truncatedMsg = HexUtil.decodeHex("01020304"); // too short
    ChannelBuffer buf = ChannelBuffers.wrappedBuffer(truncatedMsg);
    
    assertThrows(IndexOutOfBoundsException.class, () -> {
        decoder.parsePositionData(buf, null);
    });
}
```

### Incorrect Example (what to avoid):
```java
// WRONG: Only testing with complete, valid messages
@Test
public void testDecode() {
    HomtecsProtocolDecoder decoder = new HomtecsProtocolDecoder(new HomtecsProtocol());
    byte[] validMsg = HexUtil.decodeHex("...complete valid hex...");
    ChannelBuffer buf = ChannelBuffers.wrappedBuffer(validMsg);
    
    Position position = decoder.parsePositionData(buf, null);
    assertNotNull(position);  // Only validates happy path
    // NO test for truncated/invalid messages
}
```