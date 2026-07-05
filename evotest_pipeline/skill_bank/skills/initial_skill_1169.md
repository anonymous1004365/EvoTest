---
name: alternative-protocol-decoding-paths
description: When a protocol frame decoder has alternative decoding paths that may incorrectly process data, test each path independently with representative inputs to ensure correct frame construction and decoding.
code_tags: ['ARGUMENT_VALIDATION', 'NULL_CHECK', 'BOUNDARY_CHECK']
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoding-paths

## Instructions

# Alternative Protocol Decoding Paths

## Instructions

- WHEN the TG encounters a protocol frame decoder (e.g., `MeitrackProtocolDecoder`) that has multiple decoding paths (e.g., an `if-else` or `switch` on header bytes to determine protocol variant/format)
- THEN the TG should write a **parametric test** that exercises each alternative decoding path with representative byte buffer inputs, constructing and invoking the decoder's `decode` or `decodeFrame` method directly, and verifying that:
  - Each path produces a correctly parsed/framed result (e.g., `ByteBuf` with the right readable bytes)
  - The end-of-frame or length calculation is correct for each path
  - The test covers boundary conditions like minimal valid frame, empty payload, or non-standard header values

- **Common pitfall to avoid**: Testing only the "happy path" (the most common protocol variant) while leaving alternative code paths untested. The alternative path may have subtle bugs in length computation, offset handling, or byte ordering.

- **Specific example from buggy code**: In a `MeitrackProtocolDecoder`, the `decodeFrame` method may have an `if (buf.getUnsignedShort(buf.readerIndex()) == 0x2020)` branch for binary frames and an `else` branch for text-based frames. The TG should test BOTH branches:
  - A `ByteBuf` starting with `0x2020` to trigger the binary frame path
  - A `ByteBuf` starting with other bytes (e.g., text mode) to trigger the text frame path
  - Verify the returned frame has the expected readable bytes for each case

- **Incorrect approach**: Writing only one test that happens to exercise only one decoding path, assuming the other path works correctly without verification.
- **Correct approach**: Using a `@Parameters`-annotated method with test cases for each protocol variant, explicitly naming each case (e.g., `"binary frame"`, `"text frame"`), and asserting on frame length or content per case.

```java
// CORRECT: Parametric test covering both decoding paths
@Parameters(name = "{0}")
public static Iterable<Object[]> data() {
    return Arrays.asList(new Object[][]{
        {"binary frame", Unpooled.wrappedBuffer(new byte[]{0x20, 0x20, 0x00, 0x05, 0x01, 0x02, 0x03}), 5},
        {"text mode frame", Unpooled.wrappedBuffer("@@some_text\r\n".getBytes(StandardCharsets.US_ASCII)), 12},
    });
}

@Test
public void testDecodeFrame() {
    ByteBuf frame = decoder.decodeFrame(null, input);
    assertNotNull(frame);
    assertEquals(expectedReadableBytes, frame.readableBytes());
}
```

```java
// INCORRECT: Only testing one path
@Test
public void testBinaryFrameOnly() {
    ByteBuf input = Unpooled.wrappedBuffer(new byte[]{0x20, 0x20, 0x00, 0x05, 0x01, 0x02, 0x03});
    ByteBuf frame = decoder.decodeFrame(null, input);
    assertEquals(5, frame.readableBytes());
}
```