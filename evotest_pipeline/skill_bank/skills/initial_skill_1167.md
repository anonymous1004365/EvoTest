---
name: alematics-protocol-frame-decoder-switch
description: When a protocol decoder switches frame decoders between channels (e.g.,
  UDP vs TCP), test that both paths correctly decode messages. The bug occurs when
  getFrameDecoder() returns different decoders for different channels, and the alternative
  path is broken.
code_tags:
- NULL_CHECK
- VALIDATION
- PROTOCOL_FRAME_DECODING
test_pattern: PARAMETRIC_TEST
---

# alematics-protocol-frame-decoder-switch

## Instructions

# Alematics Protocol Frame Decoder Switch Bug

## Instructions

- WHEN the TG encounters a protocol decoder that calls `getFrameDecoder()` and returns different frame decoders for different channels (e.g., switching between `LengthFieldBasedFrameDecoder` and `FixedLengthFrameDecoder`, or switching decoder configurations) based on channel type, pipeline, or any conditional logic:
  - THEN the TG should write **separate tests for each unique decoder path**, ensuring that each path can successfully decode a complete message from raw bytes.
  - Include a test that sends a binary message to the alternative path (the one not used by the primary test) and assert that it decodes correctly without throwing an exception.
  - Verify that the decoded result contains the expected fields (e.g., device ID, position data, fuel level, ignition status, etc.).

- WHEN the TG writes tests for protocol decoders that use `LengthFieldBasedFrameDecoder` with specific length field offsets and lengths:
  - THEN the TG should include a test that sends binary data matching the frame format (length field at the correct offset, with correct byte order) and verify the decoder can reassemble the full frame.
  - Include in the byte array a proper length field value that accounts for the full payload length, not just partial data.

- Common pitfalls to avoid:
  - ❌ Testing only the default or primary channel path (e.g., only TCP, not UDP).
  - ❌ Using malformed binary data that doesn't match the expected frame format, causing the frame decoder to silently drop bytes or produce empty/incomplete messages.
  - ❌ Assuming `getFrameDecoder()` never changes behavior based on channel type or protocol version.
  - ❌ Not including the length field bytes in the test payload when the decoder uses `LengthFieldBasedFrameDecoder`.

- Correct example (testing alternative decoder path):
```java
@Test
public void testDecodeAlternativePath() {
    AlematicsProtocolDecoder decoder = new AlematicsProtocolDecoder(new Protocol("alematics"));
    
    String hex = "..." // valid hex string matching the format for the alternative channel
    byte[] bytes = ByteBufUtil.decodeHexDump(hex);
    
    ByteBuf buf = Unpooled.wrappedBuffer(bytes);
    SocketAddress remoteAddress = new InetSocketAddress("localhost", 0);
    
    Object result = decoder.decode(null, remoteAddress, buf);
    
    assertNotNull(result);
    assertTrue(result instanceof Position);
    Position position = (Position) result;
    assertNotNull(position.getDeviceId());
    assertEquals(expectedLat, position.getLatitude(), 0.001);
    assertEquals(expectedLon, position.getLongitude(), 0.001);
}
```

- Incorrect example (only testing the primary decoder path):
```java
// BAD: Only tests one path
@Test
public void testDecode() {
    // Only sends data for the default channel
    // Misses the alternative decoder path entirely
}
```