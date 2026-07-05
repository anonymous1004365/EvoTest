---
name: index-boundary-inequality-validation
description: When a protocol frame decoder searches for delimiter bytes using indexOf,
  it must use >= instead of > when checking if the index is valid, otherwise a frame
  starting at position 0 (beginIndex == 0) or ending at position 0 (endIndex == 0)
  is incorrectly skipped.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- BUFFER_OFFSET_HANDLING
- VALIDATION
test_pattern: STATE_TEST
---

# index-boundary-inequality-validation

## Instructions

# Index Boundary Inequality Validation

## Instructions

WHEN the TG encounters a protocol frame decoder (`extends FrameDecoder`) that uses `buf.indexOf(...)` to locate delimiter bytes, and the method checks `if (beginIndex > 0)` or `if (endIndex > 0)` before reading the frame, THEN the TG should test with input data where the delimiter appears at position 0 (e.g., immediately after an alternative decoding path resets the buffer reader index to 0).

Specifically:
- WHEN the decoder has an alternative decoding path that modifies `beginIndex` and potentially resets the `buf.readerIndex(...)` to a non-negative value (including 0), THEN the TG should verify that the decoder correctly handles a frame whose first byte is `\n` (position 0).
- The TG should construct a buffer where, after the alternative decoding logic, `beginIndex` is 0 and `endIndex` is 0 (the newline delimiter is at position 0), and verify that the decoder returns a non-null frame (does not return null and proceed to the fallback path).
- On the buggy version (using `>` instead of `>=`), the decoder will return `null` for a valid frame starting at position 0, causing data to be lost.
- On the fixed version (using `>=`), the decoder correctly recognizes index 0 as valid and returns the frame.

Common pitfalls:
- Testing only with positive indices (e.g., beginIndex > 0, endIndex > 0) and missing the edge case where indices can be 0.
- Assuming that `indexOf` never returns 0 for valid scenarios — in channel buffers, position 0 is a legitimate location for data.
- Not constructing a test where the alternative decoding path sets `beginIndex = 0` and the newline delimiter is at that same position.

### Correct example (what to write)

```java
@Test
public void testDecodeFrameWithDelimiterAtPositionZero() {
    TmgFrameDecoder decoder = new TmgFrameDecoder();
    // Simulate: alternative decoding path sets buffer to start, delimiter at position 0
    ChannelBuffer buf = ChannelBuffers.wrappedBuffer(new byte[] { '\n', 'H', 'e', 'l', 'l', 'o' });
    // Reader index may be at 0 after alternative path processing
    Object frame = decoder.decode(null, null, buf);
    // Should return a non-null frame for the content before the delimiter
    assertNotNull("Frame should be decoded when delimiter is at position 0", frame);
}
```

### Incorrect example (what to avoid)

```java
@Test
public void testDecodeFrame() {
    TmgFrameDecoder decoder = new TmgFrameDecoder();
    // Only tests with delimiter at position > 0 — misses the edge case
    ChannelBuffer buf = ChannelBuffers.wrappedBuffer(new byte[] { 'A', 'B', '\n', 'D', 'a', 't', 'a' });
    buf.readByte(); // advance reader index so beginIndex > 0
    Object frame = decoder.decode(null, null, buf);
    assertNotNull(frame); // This works, but misses beginIndex == 0 case
}
```