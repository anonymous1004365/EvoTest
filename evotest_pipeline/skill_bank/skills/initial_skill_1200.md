---
name: protocol-frame-decoder-alternative-path
description: When a protocol frame decoder has an alternative decoding path (e.g., non-standard frames or probe messages) that bypasses normal field initialization, tests must exercise both paths and verify object state is consistent. Despite limited view, the TG should test with messages that trigger the alternative path and assert that no NullPointerException or corrupted state occurs.
code_tags: ['VALIDATION', 'STATE_MUTATION', 'NULL_CHECK']
test_pattern: PARAMETRIC_TEST
---

# protocol-frame-decoder-alternative-path

## Instructions

# Protocol Frame Decoder Alternative Path Validation

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `AstraProtocolDecoder`) that decodes frames from a channel buffer, especially one that has an `isOdd()` or `isEven()` frame detection method, AND there are multiple decoding paths (one for standard frames, another for non-standard/probe messages like `0x00` long messages):
  - THEN the TG should write a parametric test that sends input data triggering BOTH the standard and the alternative (non-standard/probe) decoding paths.
  - The test MUST verify that after executing the alternative path, the decoder's internal state (e.g., fields like `time`, `index`, `command`, or other decoded attributes) is not corrupted — specifically, if two protocol messages are concatenated in the same buffer, the decoder must correctly reset between frames.
  - On the buggy version, concatenating a non-standard frame followed by a standard frame should throw a `NullPointerException` or produce an `ArrayIndexOutOfBoundsException` because the decoder's state from the first frame interferes with the second frame's decoding (e.g., `index` being too large for a subsequent array access, or a `time` field being `null` when dereferenced).
  - The TG MUST NOT assume that all frames in a protocol are of the same type — test with heterogeneous message sequences (probe + standard, standard + probe).
  - Common pitfall: Testing only a single standard frame and assuming the decoder works for all frame types. The TG must explicitly test edge cases where the frame type alternates and where the alternative path doesn't fully initialize decoder state.
- Concrete example (based on the `Astra` protocol):
  ```java
  // CORRECT: Tests concatenation of non-standard + standard frames
  @Test
  public void testDecodeMixedFrames() {
      AstraProtocolDecoder decoder = new AstraProtocolDecoder(...);
      ByteBuf buf = Unpooled.buffer();
      // Non-standard (probe) frame header
      buf.writeByte(0x00);
      buf.writeLong(0L);  // probe message
      // Standard frame
      buf.writeByte(0x01);  // non-odd frame
      buf.writeBytes(...); // valid standard frame data

      assertThrows(NullPointerException.class, () -> {
          decoder.decode(null, null, buf);
      });
  }
  ```
  ```java
  // INCORRECT: Only tests a single standard frame, doesn't trigger the alternative path
  @Test
  public void testDecodeStandardFrame() {
      // This passes even on buggy version — not catching the bug
  }
  ```
- The test pattern should be **PARAMETRIC_TEST**: use `@ParameterizedTest` with multiple frame type combinations as inputs if possible, to exercise all decoding path combinations (e.g., `{standard, standard}`, `{probe, standard}`, `{standard, probe}`, `{probe, probe}`).