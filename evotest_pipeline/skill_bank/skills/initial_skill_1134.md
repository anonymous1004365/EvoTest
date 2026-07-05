---
name: alternative-protocol-frame-decoder
description: When a protocol decoder has multiple decoding branches (e.g., frame decoding based on message type or length), the test generator must verify each branch processes data correctly and does not throw unexpected exceptions like ArrayIndexOutOfBoundsException.
code_tags: ['NULL_CHECK', 'ARGUMENT_VALIDATION', 'STATE_MUTATION', 'ALTERNATIVE_PROTOCOL_DECODING']
test_pattern: EXCEPTION_TEST
---

# alternative-protocol-frame-decoder

## Instructions

# Alternative Protocol Frame Decoder Testing

## Instructions

- WHEN the TG encounters a protocol decoder class (e.g., `TytanProtocolDecoder`) that contains conditional branching during frame decoding (e.g., `if` statements based on buffer length, message type, or byte patterns)
- THEN the TG should write parameterized tests that feed each distinct decoding branch with realistic binary data that triggers that branch's execution path
- WHEN the branching condition involves comparing buffer length against a threshold (e.g., `buf.readableBytes()` compared to `FrameDecoder` or method-level checks)
- THEN the TG should construct buffer data that is exactly at the boundary and below the boundary to trigger all branching paths
- WHEN a branch performs byte-level operations (e.g., `getUnsignedShort`, `readUnsignedShort`, `indexOf`) on a buffer
- THEN the TG must ensure the buffer has enough data for all read operations in that branch — buffers that are too short can cause `ArrayIndexOutOfBoundsException` or `IndexOutOfBoundsException`
- Common pitfalls:
  - Testing only one branch (e.g., only the happy path with well-formed data)
  - Not testing short/malformed buffers that enter a branch but lack required byte content
  - Not using different binary payloads for each branch path

### Example (Correct approach for a multi-branch decoder):
```java
// Test branch A: short buffer entering first branch → expect exception
@Test
public void testDecodeBranchAShortBuffer() {
    TytanProtocolDecoder decoder = new TytanProtocolDecoder(null);
    ByteBuf buf = Unpooled.buffer();
    buf.writeByte(0x01); // only 1 byte, branch A expects more
    assertThrows(Exception.class, () -> {
        decoder.decode(null, null, buf);
    });
}

// Test branch B: buffer data that enters second branch
@Test
public void testDecodeBranchB() {
    TytanProtocolDecoder decoder = new TytanProtocolDecoder(null);
    ByteBuf buf = Unpooled.buffer();
    // Write enough bytes for the second branch to process
    buf.writeShort(0x0200);
    buf.writeBytes(new byte[10]);
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
}
```

### Example (Incorrect — only happy path):
```java
// WRONG: Only tests one branch, does not cover alternative decoding paths
@Test
public void testDecode() {
    TytanProtocolDecoder decoder = new TytanProtocolDecoder(null);
    ByteBuf buf = Unpooled.copiedBuffer("full valid message".getBytes());
    Object result = decoder.decode(null, null, buf);
    assertNotNull(result);
    // No test for alternative branch, no test for short buffers
}
```