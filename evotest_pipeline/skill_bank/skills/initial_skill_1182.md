---
name: alternative-protocol-decoding-test
description: Tests for protocol decoders that use multi-phase or fallback decoding paths where one path may produce incomplete or wrong output. Apply when a decoder has a second decoding phase that processes the output of a first phase, often via chained handler methods.
code_tags: ['ALTERNATIVE_PROTOCOL_DECODING', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-test

## Instructions

# Alternative Protocol Decoding: Multi-Phase Fallback Validation

## Instructions

- WHEN the TG encounters a protocol decoder that uses a **multi-phase or fallback decoding path** — e.g., a `decode` method that delegates to another `decode` overload, or a decoder chain where the first handler's output is fed into a second handler — THEN the TG should:

  1. **Identify all decoding phases**: Look for methods like `decode(ChannelHandlerContext, Object)` that call `super.decode(...)` and then perform additional logic, or `decode(ChannelHandlerContext, Channel, SocketAddress, Object)` that branches based on message type/format.
  
  2. **Test the alternative/fallback path in isolation**: Craft input that specifically exercises the fallback/second-phase path rather than just the primary path. For example, if the decoder first tries to parse a message as one type and falls back to another, provide input that triggers the fallback.

  3. **Verify the final decoded result is complete and correct**: Compare the output object's fields (device ID, time, position, status, etc.) against the expected values from the original message — do not assume the fallback path preserves all fields.

  4. **Expect exceptions on invalid/corrupt input for the fallback path**: Test with malformed messages that would pass the primary decoder but break the fallback decoder.

- WHEN testing protocol decoders that produce position/device data objects, THEN verify that all essential fields (e.g., `deviceId`, `position`, `time`, `status`, `attributes`) are set correctly — do NOT test only the primary path and assume the fallback path behaves identically.

- Common pitfalls to avoid:
  - ❌ Testing only the primary decoding path when an alternative/fallback path exists
  - ❌ Assuming the fallback path sets the same fields as the primary path
  - ❌ Only testing with valid/good-format messages and ignoring boundary or malformed inputs for the fallback
  - ❌ Not testing the full decoded object, only checking that no exception is thrown

- Example of correct test approach:
```java
// Test that exercises the secondary/fallback decoding path
@Test
public void testDecodeWithAlternativeMessageFormat() {
    Tt8850ProtocolDecoder decoder = new Tt8850ProtocolDecoder(new Tt8850Protocol());
    ByteBuf buf = Unpooled.copiedBuffer("!AUTOSTOP,02,SOME,MSG,1234567890\r\n", StandardCharsets.US_ASCII);
    
    // Decode via the channel handler context path that triggers fallback logic
    Object result = decoder.decode(null, null, buf);
    
    assertTrue("Result should be a position object", result instanceof Position);
    Position position = (Position) result;
    assertEquals("Device ID should be parsed", "1234567890", position.getDeviceId());
    // Verify more fields that should be populated by the fallback path
}
```

- Example of incorrect test approach:
```java
// ❌ Only tests the primary decoding path
@Test
public void testDecode_OnlyPrimaryPath() {
    Tt8850ProtocolDecoder decoder = new Tt8850ProtocolDecoder(new Tt8850Protocol());
    ByteBuf buf = Unpooled.copiedBuffer("!PRIMARY,FORMAT,MSG\r\n", StandardCharsets.US_ASCII);
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result); // Does not verify fields set by fallback path
}
```