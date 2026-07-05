---
name: protocol-frame-decoder-alternative-path
description: ''
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- ALTERNATIVE_PROTOCOL_DECODING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# protocol-frame-decoder-alternative-path

## Instructions

# Protocol Frame Decoder Alternative Path Testing

## Instructions

**WHEN** the TG encounters a `FrameDecoder` (or any decoder extending `IoSession`, `IoHandler`, or network protocol decoder classes) that contains multiple conditional branches for determining frame length — for instance, an `if-else` or `switch` that decodes differently based on the content of the `IoBuffer`, a message header, or a state flag — **THEN** the TG should:

1. **Identify each distinct decoding branch** in the frame decoder's `decode` method (e.g., a primary path and a fallback/alternative path).
2. **Craft separate test messages** that exercise each branch independently, providing the exact byte-level data (as hex strings or `ByteBuffer`/`IoBuffer`) that triggers each branch condition.
3. **For each branch, verify that the decoded frame has the correct length and content**, by checking:
   - The length value returned by the decoder (e.g., `assertEquals(expectedLength, decodedLength)`).
   - That the remaining buffer content after decoding is as expected (e.g., the end-of-frame data matches).
4. **For the alternative/fallback branch specifically**, test with:
   - A buffer that does NOT match the primary branch's condition.
   - Edge-case buffer lengths (e.g., buffers that are exactly at a threshold, buffers that are too short to contain a header).

**Common pitfalls to avoid:**
- **Testing only the primary decoding path** while ignoring the fallback/alternative branch that actually may be buggy.
- **Using non-binary or incomplete test data** — always provide complete hex-encoded byte sequences that represent real protocol frames.
- **Relying only on mock objects** — prefer real byte buffers (`IoBuffer.wrap(...)`) that simulate actual network input.
- **Forgetting buffer position/reset** — test that the buffer's position is correctly advanced after decoding (not left at a stale offset).

### Correct Example (hypothetical)
```java
// FrameDecoder with two branches:
// Branch 1: if buffer contains marker 0xAA, length = 10 bytes
// Branch 2 (alternative): else length = buffer.remaining()
IoBuffer primaryMsg = IoBuffer.wrap(new byte[] {0x00, (byte)0xAA, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08});
int primaryLen = decoder.decode(primaryMsg);
assertEquals(10, primaryLen);

IoBuffer altMsg = IoBuffer.wrap(new byte[] {0x01, 0x02, 0x03, 0x04, 0x05});
int altLen = decoder.decode(altMsg);
assertEquals(3, altLen);  // buffer.remaining() = 3 after offset skip
```

### Incorrect Example
```java
// Only testing primary branch — buggy alternative path goes undetected
IoBuffer msg = IoBuffer.wrap(new byte[] {0x00, (byte)0xAA, 0x01, 0x02, 0x03});
int len = decoder.decode(msg);
// Bug: alternative branch for non-0xAA buffers returns wrong length,
// but no test covers that path.
```