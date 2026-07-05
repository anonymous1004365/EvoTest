---
name: alternative-protocol-decoding-path
description: Tests protocol frame decoding where the decoder has an alternative decoding path that may crash or return wrong results. Use when testing custom protocol decoders with multiple decode branches.
code_tags: ['NULL_CHECK', 'ARGUMENT_VALIDATION', 'STATE_MUTATION']
test_pattern: EXCEPTION_TEST
---

# alternative-protocol-decoding-path

## Instructions

# Alternative Protocol Decoding Path

## Instructions

- WHEN the TG encounters a protocol decoder class that has multiple decoding branches (e.g., checking some condition and choosing between two different decoding logics, such as via `if`/`else` on a field or configuration flag)
- THEN the TG should write a test that exercises **each alternative decoding path** with realistic binary input buffers, verifying that no exception (e.g., `IndexOutOfBoundsException`, `ArrayIndexOutOfBoundsException`, `BufferUnderflowException`, `NullPointerException`) is thrown and that the decoded result is non-null and correct on the fixed version.
- Include concrete examples using the actual buffer type (e.g., `ChannelBuffer`, `ByteBuf`, `ByteBuffer`) with known byte sequences aligned to the protocol format.
- Test both paths: the primary path and the alternative path. Do not assume the primary path is the only one used.
- **Common pitfall**: Testing only one decoding branch (usually the normal/primary path) and missing the alternative path that may lack proper bounds checking or state validation before accessing the buffer.
- **Example of a correct test pattern**:
```java
// Test alternative decoding path (e.g., when some flag/condition is met)
@Test
public void testDecodeAlternativePath() {
    SmokeyProtocolDecoder decoder = new SmokeyProtocolDecoder();
    // Build a buffer with data that triggers the alternative branch
    ByteBuf buf = Unpooled.buffer();
    buf.writeByte(/* header byte triggering alt path */);
    buf.writeBytes(/* payload bytes */);
    Object result = decoder.decode(null, null, buf);
    assertNotNull("Decode result should not be null", result);
}
```
- **Example of an incorrect test pattern** (the pitfall):
```java
// WRONG: Only tests the primary/default path, missing the alternative branch
@Test
public void testDecodeDefault() {
    SmokeyProtocolDecoder decoder = new SmokeyProtocolDecoder();
    ByteBuf buf = Unpooled.buffer();
    // Only write default-format data without covering the alternative branch
    buf.writeInt(12345);
    assertNotNull(decoder.decode(null, null, buf));
}
```