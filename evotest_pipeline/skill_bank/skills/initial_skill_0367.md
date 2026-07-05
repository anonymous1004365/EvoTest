---
name: protocol-frame-length-calculation
description: When encoding protocol frames with a length field, verify that the length
  calculation includes exactly the right fields — not extra constant offsets. This
  skill applies to packet encoding where the frame length is written as a 2-byte short
  value before the payload.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# protocol-frame-length-calculation

## Instructions

# Protocol Frame Length Calculation

## Instructions

- WHEN the TG encounters a protocol encoder that writes a length field (e.g., `result.writeShort(...)`) immediately before variable-length payload data in a packet structure
- THEN the TG should verify the length calculation includes only the payload bytes (`buf.readableBytes()`) plus any fixed-size header fields that actually come BEFORE the length field, but NOT fields that follow the length field (like checksum, status, etc.)
- Specifically, WHEN the encoder writes a header sequence (e.g., `'E'`, `'L'`), then a length short, then a checksum short, then the payload: the length field should equal `(2 bytes for header) + (buf.readableBytes() for payload)` — NOT `(2 + 2 + 2 + buf.readableBytes())` which incorrectly includes the length field itself (2) and the checksum field (2)
- The TG MUST write a test that creates an `EelinkProtocolEncoder` instance, sets up a `ChannelHandlerContext` with a mock `Channel` returning `true` for `isActive()`, then sends a command (like a `TextCommand` with keyword "status") and verifies the encoded buffer has the correct total packet size, OR use a ChannelOutboundHandlerAdapter test pattern that captures written data and validates the length short value
- Common pitfalls to avoid: (1) assuming the length field includes the entire packet instead of just the payload + preceding headers; (2) forgetting that the `result.writeShort(length)` itself writes 2 bytes that are NOT counted in the length value; (3) testing only non-connectionless code paths and missing the connectionless bug entirely; (4) not verifying the specific byte values of the length field using buffer inspection

### Correct test approach
```java
// Create an encoder instance
EelinkProtocolEncoder encoder = new EelinkProtocolEncoder();

// Set up pipeline with EmbeddedChannel
EmbeddedChannel channel = new EmbeddedChannel(encoder);

// Send a command
channel.writeOutbound(new TextCommand("status"));

// Read the encoded message
ByteBuf encoded = channel.readOutbound();

// Verify length field at offset 2 (after 'E', 'L' headers)
int actualLength = encoded.getUnsignedShort(2);
int expectedPayloadLength = encoded.readableBytes() - 4; // 2 header + 2 length = 4 bytes before payload
// Or, if the payload includes checksum: check that length == buf.readableBytes() + 2 (only headers before length)
// The key is: length should NOT include the length field itself (2) nor the checksum field (2)
```

### Incorrect test approach (would miss the bug)
```java
// Testing only a non-connectionless path (default encoder path)
// OR testing without inspecting the actual length field value
EmbeddedChannel channel = new EmbeddedChannel(encoder);
channel.writeOutbound(new TextCommand("status"));
ByteBuf buf = channel.readOutbound();
// Just checking buf is not null — this misses the length miscalculation
assertNotNull(buf);
```