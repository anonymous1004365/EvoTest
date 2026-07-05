---
name: alternative-protocol-decoder-boundary
description: When a frame decoder has an alternative/fallback decoding path, test
  that alternative path with partial and edge-case messages to ensure frame boundaries
  are correctly identified. This skill prevents bugs where alternative decode logic
  misidentifies message lengths or end-of-frame markers.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# alternative-protocol-decoder-boundary

## Instructions

# Alternative Protocol Decoder Frame Boundary Testing

## Instructions

- WHEN the TG encounters a network protocol frame decoder class (e.g., `H02FrameDecoder`) that has an alternative or fallback decoding path (e.g., `decodeAlternative` method or an alternative branch in `decode`)
- THEN the TG MUST write a parametric test that:
  1. Creates real buffer inputs (e.g., `ChannelBuffer`) representing various message formats that the alternative path would process
  2. Tests the alternative path directly by calling it with these buffers (e.g., `decoder.decodeAlternative(buf)`) or by feeding crafted input through the main `decode` method so it triggers the alternative branch
  3. Verifies that each input produces the correct decoded frame (length, content, end-of-frame position)
  4. Includes edge cases such as:
     - Empty buffers or buffers with only partial data (e.g., missing end-of-frame marker)
     - Buffers with exactly the minimum valid message length
     - Buffers with multiple valid messages concatenated
     - Buffers with unexpected or malformed data that should fail gracefully (e.g., return `null`)
- WHEN the alternative path looks for a specific byte pattern to mark end-of-frame (e.g., a newline `'\n'` = `0x0A` or other marker)
- THEN the TG MUST also test:
  - Messages that contain the marker byte within the payload (not just as terminator) — these should not cause premature frame termination
  - Messages where the marker appears in different positions (beginning, middle, end)
- COMMON PITFALLS to avoid:
  - Testing only the main decoding path and assuming the alternative path behaves identically
  - Testing only happy-path messages and not edge cases like empty/partial/malformed input
  - Using in-memory objects instead of real `ChannelBuffer`/`ByteBuf` wrappers — the decoder may check buffer internals (readable bytes, reader index, etc.)
  - Not verifying that failed decode attempts leave the buffer in a valid state (reader index correctly reset)
  - Not testing with both valid and invalid alternative-format messages side by side

### Example (Correct — Catches the Bug)

```java
@Test
public void testDecodeAlternative() {
    H02FrameDecoder decoder = new H02FrameDecoder();
    
    // A message that follows the alternative format
    ChannelBuffer buf = ChannelBuffers.wrappedBuffer(new byte[] {
        0x50, 0x51, 0x52, (byte) 0x0A  // valid message ending with \n
    });
    
    Object result = decoder.decode(null, null, buf);
    assertNotNull("Alternative decode should produce a result", result);
    
    // A partial message without end marker — should return null or not consume
    ChannelBuffer partialBuf = ChannelBuffers.wrappedBuffer(new byte[] {
        0x50, 0x51  // missing \n terminator
    });
    Object partialResult = decoder.decode(null, null, partialBuf);
    assertNull("Partial message should return null/fail", partialResult);
}
```

### Example (Incorrect — Misses the Bug)

```java
// BAD: Only tests the main decoding path, not the alternative
@Test
public void testDecodeMainOnly() {
    H02FrameDecoder decoder = new H02FrameDecoder();
    ChannelBuffer buf = ChannelBuffers.wrappedBuffer(new byte[] { 0x48, 0x02, 0x00, 0x05 });
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
    // This test passes on both buggy and fixed versions, missing the regression entirely
}
```