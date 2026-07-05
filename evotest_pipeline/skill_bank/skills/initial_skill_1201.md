---
name: protocol-alternative-decoder-buffer-advancement
description: When a protocol decoder has an alternative decoding path that prematurely
  advances the buffer's reader index without fully consuming a frame, remaining data
  for subsequent frames gets skipped or misaligned. Apply this skill when a decoder
  detects frame boundaries via delimiters and has fallback parsing logic.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
test_pattern: PARAMETRIC_TEST
---

# protocol-alternative-decoder-buffer-advancement

## Instructions

# Protocol Alternative Decoder Buffer Advancement

## Instructions

- WHEN the TG encounters a protocol decoder that:
  1. Detects frame boundaries using a delimiter/marker pattern in the buffer (e.g., checking for specific bytes like 0xFE, 0xFD, or reading a frame header)
  2. Has an alternative/fix-up decoding path that adjusts the buffer's `readerIndex` (e.g., `buffer.readerIndex()`) after determining the frame type or header
  3. Processes the frame body differently depending on some header field (e.g., a protocol version, message type, or format indicator)

- THEN the TG should verify that when a frame with a certain header format is decoded using the alternative path, the buffer's `readerIndex` is correctly positioned at the END of the current frame — NOT advanced partially or incorrectly — so that when multiple frames are concatenated in the same buffer, all subsequent frames are still decodable.

  Specifically, write a test that:
  - Concatenates TWO or more complete protocol frames in a single ByteBuf, where the FIRST frame triggers the alternative decoding path (e.g., has a specific message type, version field, or format that causes the decoder to take the fix-up branch)
  - Calls the decoder's `decode()` method once with the concatenated buffer
  - Verifies that ALL frames are successfully decoded and returned as a list of objects
  - The test MUST assert that the number of decoded objects equals the number of distinct frames in the buffer (e.g., `assertEquals(2, decodedObjects.size())`)
  - Capture any exception thrown: on the buggy version, the second frame will fail to decode (e.g., `IndexOutOfBoundsException` or returning only 1 object) because the alternative path incorrectly advanced the readerIndex beyond the first frame boundary

- Common pitfalls to avoid:
  - Testing only a single frame in isolation — this will NOT catch the buffer advancement bug
  - Testing only the content (fields) of the decoded message without checking that ALL messages in the buffer were decoded
  - Using a `ByteBuf` with only one frame and calling `decode()` multiple times sequentially — the bug manifests only when multiple frames are already concatenated in a single buffer
  - Forgetting to reset the buffer's `readerIndex` to 0 before passing to the decoder (if the decoder expects to start from index 0)
  - Assuming that decoding a single frame correctly implies that multi-frame decoding works

- Example of a CORRECT test (pseudocode):

```java
@Test
public void testDecodeMultipleFramesWithAlternativePath() {
    FifotrackProtocolDecoder decoder = new FifotrackProtocolDecoder(null);
    ByteBuf buffer = Unpooled.buffer();
    
    // Frame 1: triggers the alternative decoding path (e.g., format indicator = 1)
    buffer.writeBytes(ByteBufUtil.decodeHexDump("010203FE..."));
    // Frame 2: normal decoding path
    buffer.writeBytes(ByteBufUtil.decodeHexDump("040506FE..."));
    
    Object result = decoder.decode(null, null, buffer);
    
    // Verify BOTH frames were decoded
    assertTrue(result instanceof List);
    assertEquals(2, ((List) result).size());
}
```

- Example of an INCORRECT test (does NOT catch the bug):

```java
@Test
public void testDecodeSingleFrame() {
    FifotrackProtocolDecoder decoder = new FifotrackProtocolDecoder(null);
    ByteBuf buffer = Unpooled.buffer();
    buffer.writeBytes(ByteBufUtil.decodeHexDump("010203FE..."));
    
    Object result = decoder.decode(null, null, buffer);
    assertTrue(result instanceof List);
    assertEquals(1, ((List) result).size()); // This passes even with the bug!
}
```