---
name: protocol-decoder-alternative-parse-path
description: WHEN a protocol decoder has multiple alternative parsing paths (e.g. different frame formats), THEN test that ALL paths produce complete and correct decoded positions. The bug was that one parsing path silently skipped data when the alternative path failed, causing incomplete decoding that wasn't detected.
code_tags: ['PROTOCOL_DECODER_FRAME_HANDLING', 'ALTERNATIVE_PROTOCOL_DECODING', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-alternative-parse-path

## Instructions

# Protocol Decoder Alternative Parse Path — Silent Data Loss

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g. `NvsProtocolDecoder`) that contains multiple alternative decoding branches or paths (e.g. different frame formats, multiple `if/else` or `try/catch` blocks handling different protocol variants)
- THEN the TG should write a parametric test that sends malformed or incomplete data to the decoder **via each alternative path**, and verify that ALL paths still produce a complete decoded result (or the expected exception). Specifically:
  - For each alternative decoding branch, construct a binary input that triggers that specific branch
  - Send the input to the decoder (e.g. `NvsProtocolDecoder.decode(...)`)
  - Assert that the decoded position (e.g. the `ChannelBuffer` reader index) has moved forward past the consumed data — **not** stuck at the start — unless the decoder deliberately returns `null` for unsupported data
  - Verify that the decoded object contains the expected fields (e.g. device ID, time, position) for each alternative path
- **Common pitfalls:**
  - Testing only the "happy path" (the first/formatted frame type) and forgetting to test alternative parsing paths
  - Assuming that if the decoder returns a non-null result, all data was consumed — the bug might cause partial consumption (silent skip) even with a non-null return
  - Not checking the `ChannelBuffer`/`ByteBuf` reader index after decoding to confirm all bytes were consumed
  - Relying only on a single test case — use a parametrized test with multiple inputs, one per alternative parsing path

### Correct Example (Parametrized Test)

```java
@ParameterizedTest
@CsvSource({
    "'<FIRST_FRAME_HEX_DATA>', '<expectedDeviceId>', '<expectedLat>', '<expectedLon>'",
    "'<SECOND_ALTERNATIVE_FRAME_HEX_DATA>', '<expectedDeviceId>', '<expectedLat>', '<expectedLon>'"
})
void testDecodeAllPaths(String hexData, String expectedId, double expectedLat, double expectedLon) {
    NvsProtocolDecoder decoder = new NvsProtocolDecoder(null);
    ChannelBuffer buf = ChannelBuffers.copiedBuffer(ByteBufUtil.decodeHexDump(hexData));
    Object decoded = decoder.decode(null, null, buf);
    assertNotNull("Decoder should not return null for valid input", decoded);
    assertTrue("All bytes should be consumed", buf.readableBytes() == 0);
    // Or at minimum: assertTrue("Reader index should advance past data", buf.readerIndex() > 0);
    assertTrue(decoded instanceof Position);
    Position pos = (Position) decoded;
    assertEquals(expectedId, pos.getDeviceId());
    assertEquals(expectedLat, pos.getLatitude(), 0.0001);
    assertEquals(expectedLon, pos.getLongitude(), 0.0001);
}
```

### Incorrect Example (Only Happy Path, No Parametric, No Reader Index Check)

```java
@Test
void testDecode() {
    NvsProtocolDecoder decoder = new NvsProtocolDecoder(null);
    // Only tests one path — misses the alternative path bug
    String hexData = "<ONLY_FIRST_PATH_DATA>";
    ChannelBuffer buf = ChannelBuffers.copiedBuffer(ByteBufUtil.decodeHexDump(hexData));
    Object decoded = decoder.decode(null, null, buf);
    assertNotNull(decoded);
    // Missing: check buf.readerIndex()/readableBytes() — could silently skip data
}
```