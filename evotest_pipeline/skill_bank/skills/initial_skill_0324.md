---
name: buffer-argument-length-validation
description: WHEN the TG encounters methods that process buffer/array data with associated
  length parameters from external inputs THEN it should verify that the length parameter
  does not exceed the actual buffer capacity, as mismatches can cause infinite loops
  or buffer overflows.
code_tags:
- NULL_CHECK
- SET_OPERATION_MATH
- ALTERNATIVE_PROTOCOL_DECODING
- BUFFER_OFFSET_HANDLING
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# buffer-argument-length-validation

## Instructions

# Buffer Argument Length Validation

## Instructions

- WHEN the TG encounters a method that accepts a buffer (byte[], ByteBuf, etc.) along with separate offset and length parameters that control how much data to process from the buffer
- THEN the TG should write tests where the declared length parameter exceeds the actual buffer capacity, verifying that the method either:
  - Throws an appropriate exception (e.g., IllegalArgumentException, IndexOutOfBoundsException)
  - Handles the mismatch gracefully without entering an infinite loop or crashing
- Include tests where the `length` parameter is larger than `buffer.length - offset` or larger than the buffer's readable bytes, to verify proper bounds checking
- A common mistake (pitfall) is testing only with well-formed inputs where the length matches the buffer, missing the case where length is invalid/larger than the buffer capacity
- Another common mistake is testing only null/empty buffers but not mismatched length parameters

### Example (Correct):
```java
@Test
public void testDecodeWithInvalidLength() {
    TotemFrameDecoder decoder = new TotemFrameDecoder();
    ByteBuf buf = Unpooled.buffer();
    buf.writeByte(0x00);
    // Length (buf.readableBytes() + extra) exceeds actual buffer content
    // expected to throw an exception or be handled gracefully
    assertThrows(Exception.class, () -> {
        decoder.decode(null, buf, null);
    });
}
```

### Example (Incorrect - missing validation):
```java
@Test
public void testDecode() {
    TotemFrameDecoder decoder = new TotemFrameDecoder();
    ByteBuf buf = Unpooled.copiedBuffer(new byte[]{0x01, 0x02, 0x03});
    // Only tests with perfectly sized buffer — misses the case where
    // length declared in the data doesn't match actual buffer size
    assertNotNull(decoder.decode(null, buf, null));
}
```