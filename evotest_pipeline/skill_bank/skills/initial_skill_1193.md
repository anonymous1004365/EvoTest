---
name: protocol-decoder-frame-alternative-path
description: When a protocol frame decoder has an alternative/fallback decoding path
  that may produce different frame lengths, test both paths with the same input data
  to ensure they return the same result.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
- TYPE_CONVERSION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-frame-alternative-path

## Instructions

# Protocol Decoder Frame Alternative Path

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `Stl060ProtocolDecoder`) that has an alternative or fallback frame decoding path (e.g., a method like `decode` that can take different argument types, or has conditional branches for how the frame length is computed)
- THEN the TG should create **parametric tests** that exercise every decoding path with the **exact same input buffer** and assert that all paths produce the **same decoded frame length**.
- The test must create a raw byte buffer (e.g., using `Unpooled.copiedBuffer` with hex-encoded bytes via `ChannelBuffers.wrappedBuffer` or `ByteBuf`) and pass it through both the primary and alternative decoder paths.
- Specifically, verify that the return value (frame length) is identical between paths — not just non-null or positive.
- Common pitfall: Testing only the "happy path" (primary decoding logic) while ignoring the alternative branch that might return a different length. Always test both paths when an alternative/fallback exists.
- Example of what to verify:
  - Primary path: `decoder.decode(ctx, channel, buf)` returns frame length X
  - Alternative path: `decoder.decode(ctx, channel, buf, alternativeParam)` — if such an overload exists — returns frame length Y
  - Assert that `X == Y` on the fixed version, and that the test catches the bug when `X != Y` on the buggy version.
- If no overload exists, test the alternative by constructing the same input but forcing execution into a different conditional branch (e.g., by varying the buffer contents to match a `case` statement for a different device type or protocol variant).

### Correct Example
```java
// Parametric test exercising both primary and alternative decoding paths
@ParameterizedTest
@MethodSource("provideTestBuffers")
public void testDecodeFrameLengthConsistency(byte[] rawData) {
    Stl060ProtocolDecoder decoder = new Stl060ProtocolDecoder(...);
    ByteBuf buf = Unpooled.wrappedBuffer(rawData);
    int frameLen = decoder.decode(ctx, channel, buf);
    
    buf.readerIndex(0); // reset for second path
    // Use the overloaded decode method or force alternative branch
    int frameLenAlt = decoder.decode(ctx, channel, buf, someParam); 
    
    assertEquals(frameLen, frameLenAlt, 
        "Primary and alternative decode paths must return the same frame length");
}
```

### Incorrect Example
```java
// Only tests one path — the alternative path bug goes undetected
@Test
public void testDecodePrimary() {
    Stl060ProtocolDecoder decoder = new Stl060ProtocolDecoder(...);
    ByteBuf buf = Unpooled.wrappedBuffer(new byte[]{...});
    int frameLen = decoder.decode(ctx, channel, buf);
    assertTrue(frameLen > 0); // Doesn't compare with alternative path
}
```