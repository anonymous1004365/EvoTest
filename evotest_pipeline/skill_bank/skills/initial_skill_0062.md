---
name: protocol-decoder-null-unknown-data
description: For protocol decoders that may receive null, empty, or unknown data patterns,
  teach the TG to test with null buffers, empty buffers, and unexpected byte sequences
  that could trigger NullPointerException or other crashes.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- PROTOCOL_DECODER_UNKNOWN_DATA
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# protocol-decoder-null-unknown-data

## Instructions

# Protocol Decoder Null and Unknown Data Handling

## Instructions

- WHEN the TG tests a protocol decoder class that implements a `decode` method accepting a channel/handler and a byte buffer,
  - THEN the TG should write tests that pass `null` as the byte buffer argument to verify the decoder does not throw a `NullPointerException`.
  - THEN the TG should write tests that pass an empty or zero-length byte buffer to verify the decoder handles gracefully (returns `null` or an empty list without crashing).
  - THEN the TG should write tests that pass unknown, malformed, or unexpected byte sequences (e.g., random bytes, partial packets, wrong protocol identifiers) to verify the decoder returns `null` or a sensible default instead of throwing an uncaught exception.

- WHEN the decoder uses direct field access on the buffer without null checks (e.g., `buf.toString()`, `buf.readUnsignedShort()`, `buf.readableBytes()`),
  - THEN the TG must verify the decoder is resilient to `null` inputs by asserting `assertNull(result)` or catching the expected graceful failure.

- Common pitfalls:
  - Testing only valid/expected protocol messages and assuming the decoder always receives well-formed data.
  - Forgetting to test with `null` input because the API contract may not explicitly state null safety.
  - Only testing with empty buffers but not with `null` buffers, or vice versa.

- Example: When testing a decoder named `CguardProtocolDecoder`, write a test like:

```java
// Correct: Tests null and empty buffer handling
@Test
public void testDecodeWithNullBuffer() throws Exception {
    CguardProtocolDecoder decoder = new CguardProtocolDecoder();
    // Passing null as the buffer — should not throw NPE
    Object result = decoder.decode(null, null, null);
    assertNull(result);  // or similar graceful handling
}

@Test
public void testDecodeWithEmptyBuffer() throws Exception {
    CguardProtocolDecoder decoder = new CguardProtocolDecoder();
    Object result = decoder.decode(null, null, Unpooled.buffer(0));
    assertNull(result);
}

@Test
public void testDecodeWithMalformedData() throws Exception {
    CguardProtocolDecoder decoder = new CguardProtocolDecoder();
    byte[] garbage = new byte[]{0x00, 0x01, 0x02, (byte)0xFF};
    Object result = decoder.decode(null, null, Unpooled.copiedBuffer(garbage));
    assertNull(result);  // malformed data should not crash the decoder
}
```

```java
// Incorrect: Only tests with valid protocol messages, leaving null/empty paths uncovered
@Test
public void testDecodeValidMessage() throws Exception {
    CguardProtocolDecoder decoder = new CguardProtocolDecoder();
    // Only valid message — null or empty buffer would crash
    ByteBuf buf = Unpooled.copiedBuffer("valid-protocol-data", Charset.defaultCharset());
    assertNotNull(decoder.decode(null, null, buf));
}
```