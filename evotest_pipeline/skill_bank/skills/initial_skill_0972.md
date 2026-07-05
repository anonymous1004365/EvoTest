---
name: alternative-protocol-decoding
description: When a protocol decoder has multiple decoding paths (normal frame decoder
  vs. alternative decoded messages), test that the alternative path correctly parses
  and returns decoded data from the same channel. The TG should test non-standard
  protocol lengths that trigger the alternative decoding branch.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder that has both a normal frame decoder (e.g., `getFrameDecoder()`) and an alternative decoding path triggered by specific message characteristics (e.g., certain message lengths), THEN it should test that the alternative path correctly handles and decodes the messages.

- WHEN testing the alternative decoding path, THEN use a channel input buffer with the specific characteristics that trigger the alternative path (e.g., non-standard length, specific prefix bytes), and verify that the decoder correctly decodes and returns position/status data.

- WHEN the decoder returns decoded objects from the alternative path, THEN verify the returned objects contain expected field values (e.g., latitude, longitude, speed, course) using assertions on the decoded position objects.

- Common pitfalls to avoid:
  - Testing only the normal frame decoder path while ignoring the alternative decoding branch
  - Assuming the alternative path fails silently (the bug may be that it returns null or partial data instead of a properly decoded message)
  - Not covering edge cases in protocol message structure that trigger the alternative logic

### Correct Example
```java
// Test the alternative decoding path triggered by specific message length
EskyProtocolDecoder decoder = new EskyProtocolDecoder(null);
Channel channel = new EmbeddedChannel();
SocketAddress remoteAddress = new InetSocketAddress("localhost", 0);

// Create a buffer with characteristics that trigger the alternative path
ByteBuf buf = Unpooled.buffer();
buf.writeByte(0xXX); // specific prefix/trigger byte
// ... write remaining message bytes ...
buf.writeByte(END_CHAR); // end delimiter

// Decode and verify the alternative path produces valid decoded objects
Object result = decoder.decode(channel, remoteAddress, buf);
assertNotNull("Alternative path should produce decoded data", result);
assertTrue(result instanceof Position);
Position position = (Position) result;
assertNotNull(position.getLatitude());
assertNotNull(position.getLongitude());
```

### Incorrect Example (what to avoid)
```java
// BAD: Only tests the normal frame decoder path, ignores the alternative path
EskyProtocolDecoder decoder = new EskyProtocolDecoder(null);
// ... only sends messages that go through normal frame decoder ...
// Never tests the alternative path that returns decoded data directly from the channel
```