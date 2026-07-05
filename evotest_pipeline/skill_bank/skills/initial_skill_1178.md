---
name: protocol-frame-decoder-alternative-path
description: Test protocol frame decoders that have alternative decoding paths for different channel types or protocol variants, ensuring each path correctly handles frame boundaries and does not throw unexpected exceptions.
code_tags: ['PROTOCOL_FRAME_DECODING']
test_pattern: EXCEPTION_TEST
---

# protocol-frame-decoder-alternative-path

## Instructions

# Protocol Frame Decoder Alternative Path Testing

## Instructions

- WHEN the TG encounters a protocol frame decoder class (e.g., `Gps103ProtocolDecoder`) that uses `extends` from a base decoder class (e.g., `BaseFrameDecoder`) AND has an alternative decoding path (e.g., checking `channel` type or protocol variant) that returns a different result than the main path:
  - THEN the TG should write a test that exercises the alternative decoding path specifically, by passing the appropriate channel or protocol variant that triggers that path.
  - The test should verify that no exception is thrown during decoding (e.g., `NullPointerException`, `IndexOutOfBoundsException`).
  - Include concrete byte buffer payloads with realistic frame boundaries (e.g., correct frame length, checksum, delimiter) to ensure the decoder completes without error.
  - The test should use `ChannelHandlerContext` or appropriate mocking to simulate the specific channel type that triggers the alternative path.

- Common pitfalls to avoid:
  - Testing only the main/default decoding path and never exercising the alternative branch.
  - Using an incomplete or malformed buffer that would fail even on the fixed version (distinguish between "expected malformed data rejection" and "unexpected crash from alternative path").
  - Forgetting to mock or set up the channel/connection metadata that determines which decoding path is taken.

- Concrete example of what to test:
  - If the alternative path does `channel.attr(KEY).get()` or checks channel configuration, provide a channel mock that has the expected attribute.
  - Send a complete, valid protocol message (e.g., a Gps103-formatted string with correct checksum and delimiter) through the alternative decoder path.
  - Assert that decoding succeeds (returns a non-null object or passes without exception).

- Example INCORRECT test (only tests the main path):
```java
// BAD: Uses a regular channel that takes the main path,
// never triggering the alternative branch
Channel channel = new EmbeddedChannel(new Gps103ProtocolDecoder());
channel.writeInbound(buf);  // only tests the default path
```

- Example CORRECT test (exercises the alternative path):
```java
// GOOD: Sets up channel attribute/configuration that triggers 
// the alternative decoding path
Channel channel = new EmbeddedChannel(new Gps103ProtocolDecoder());
channel.attr(Gps103ProtocolDecoder.ALTERNATIVE_KEY).set(true);
channel.writeInbound(createValidGps103Buffer());
assertNotNull(channel.readInbound());
```