---
name: alternative-protocol-frame-decoder
description: When a protocol decoder has an alternative decoding path (e.g., different channels or connection types) that uses a different frame decoder, the TG should test that the alternative path correctly decodes valid messages and handles malformed data without NullPointerException.
code_tags: ['PROTOCOL_FRAME_DECODING']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-frame-decoder

## Instructions

# Alternative Protocol Frame Decoder Paths

## Instructions

- WHEN the TG encounters a protocol decoder class that has multiple decoding paths (e.g., a `MaestroProtocolDecoder` that extends `BaseProtocolDecoder` and whose constructor registers an alternative `FrameDecoder` for a specific channel/connection type like `"udp"`)
- THEN the TG should write a parametrized test that sends the same valid binary message through both the default channel and the alternative channel to verify that both paths correctly decode the message. The test should decode a known-good message (e.g., encoded as hex `0f010403040106010b640f`) and assert that the resulting position/cell tower data contains expected values (e.g., latitude, longitude, network cell reception parameters).
- WHEN the protocol has an alternative frame decoder path (e.g., a `WrappedFrameDecoder` or custom frame decoder for `"udp"` channels) and the main decoder relies on the frame decoder for buffer position management
- THEN the TG should also test with corrupt/incomplete binary data (e.g., a 2-byte partial message `0f01`) sent through the alternative channel to verify that the decoder handles it gracefully without throwing a NullPointerException or ArrayIndexOutOfBoundsException
- Common pitfalls to avoid:
  - Testing only the default channel/connection type and ignoring the alternative path
  - Assuming that a fix for the main decoding path automatically applies to alternative paths
  - Using String-based parsing instead of proper binary buffer (ByteBuf) operations
  - Not testing edge cases like empty or truncated messages on the alternative path

### Correct Example (what the TG should do):
```java
@Test
public void testDecode() throws Exception {
    MaestroProtocolDecoder decoder = new MaestroProtocolDecoder();
    
    // Test default channel
    ByteBuf buf1 = Unpooled.copiedBuffer(new byte[]{0x0f, 0x01, 0x04, 0x03, 0x04, 0x01, 0x06, 0x01, 0x0b, 0x64, 0x0f});
    Object result1 = decoder.decode(null, null, buf1);
    assertNotNull(result1);
    // ... verify position data
    
    // Test alternative channel (e.g., "udp") which may use a different FrameDecoder
    ByteBuf buf2 = Unpooled.copiedBuffer(new byte[]{0x0f, 0x01, 0x04, 0x03, 0x04, 0x01, 0x06, 0x01, 0x0b, 0x64, 0x0f});
    Object result2 = decoder.decode(null, new ChannelWithProtocol("udp"), buf2);
    assertNotNull(result2);
    // ... verify same position data
}
```

### Incorrect Example (what the TG should avoid):
```java
// BAD: Only tests default channel, not the alternative "udp" channel that uses
// a different FrameDecoder which may have a bug
@Test
public void testDecode() throws Exception {
    MaestroProtocolDecoder decoder = new MaestroProtocolDecoder();
    String message = "0f010403040106010b640f";
    // BAD: Using string parsing instead of raw binary ByteBuf
    Object result = decoder.decode(null, null, Unpooled.copiedBuffer(message.getBytes()));
    assertNotNull(result);
}
```