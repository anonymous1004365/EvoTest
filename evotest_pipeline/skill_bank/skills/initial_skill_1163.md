---
name: alternative-protocol-decoding-path
description: When a protocol decoder has alternative decoding paths that may fail silently or produce wrong results, test each alternative path separately with diverse inputs including edge cases. This skill applies to frame decoders with fallback logic.
code_tags: ['ARRAY_INDEX_ACCESS', 'ARGUMENT_VALIDATION', 'STATE_MUTATION', 'ALTERNATIVE_PROTOCOL_DECODING', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path Validation

## Instructions

- WHEN the TG encounters a protocol frame decoder (e.g., extending `FrameDecoder`, `ChannelHandler`, or implementing `ChannelInboundHandler`) that contains an **alternative decoding path** — such as a fallback branch when the primary parsing heuristic fails (e.g., when `channel.remoteAddress()` is unavailable, when a local address is null, or when a `SocketAddress` is not an `InetSocketAddress`)
- THEN the TG should write a **parametric test** that exercises **each alternative code path** separately. Specifically:
  - Test the primary/standard decoding path with a valid protocol buffer.
  - Test the alternative/fallback path by simulating the condition that triggers it (e.g., null local address, non-InetSocketAddress, missing remote address).
  - For each path, verify that the returned decoded frame is correct and that no `ClassCastException`, `NullPointerException`, or silently swallowed exception occurs.
  - Provide inputs of the correct protocol buffer type (e.g., `ByteBuf` via `Unpooled.copiedBuffer`) for each path.
  - If the fallback path uses a hardcoded or derived identifier (e.g., a device ID derived from the remote address), verify that identifier is correctly set on the decoded result.
- Common pitfalls:
  - Testing only the primary path and assuming the fallback path works identically.
  - Forgetting that a null `remoteAddress()` or non-standard `SocketAddress` subtype can trigger the alternative path at runtime.
  - Using mocked channels that always return `InetSocketAddress`, thereby never exercising the fallback.
  - Not verifying the content/identity of the decoded message (e.g., device ID, protocol type) on the alternative path.
  - Assuming the decoder produces the same output on both paths when it may produce subtly different results (e.g., different device identifiers, missing fields).

**Correct example (conceptual):**
```java
// Test primary path with standard InetSocketAddress
Channel channel = mock(Channel.class);
when(channel.remoteAddress()).thenReturn(new InetSocketAddress("192.168.1.1", 1234));
Object decoded = decoder.decode(ctx, channel, buffer);
assertNotNull(decoded);
assertEquals("expected-id", ((MyProtocolMessage) decoded).getDeviceId());

// Test fallback path with null remoteAddress
when(channel.remoteAddress()).thenReturn(null);
Object decodedFallback = decoder.decode(ctx, channel, buffer);
assertNotNull(decodedFallback);
// Verify fallback uses default/derived identifier correctly
assertEquals("fallback-id", ((MyProtocolMessage) decodedFallback).getDeviceId());
```

**Incorrect example (conceptual):**
```java
// Only tests the primary happy path — misses fallback bug
Channel channel = mock(Channel.class);
when(channel.remoteAddress()).thenReturn(new InetSocketAddress("10.0.0.1", 80));
Object decoded = decoder.decode(ctx, channel, buffer);
assertNotNull(decoded);
// No test for null remoteAddress path — will miss ClassCastException or wrong output
```