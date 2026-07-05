---
name: nio-buffer-to-primitive-conversion
description: When converting nio ByteBuffers to/from numeric primitive types (Integer,
  Long, Short, Float, Double), test that ByteBuffer.getInt()/getLong()/getDouble()/getFloat()/getShort()
  does not throw BufferUnderflowException. This applies to any ByteBuffer-based type
  converter method that allocates, puts, and flips before returning the buffer.
code_tags:
- BUFFER_OFFSET_HANDLING
- NIO_BUFFER_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# nio-buffer-to-primitive-conversion

## Instructions

# NIO Buffer to Primitive Type Conversion

## Instructions

WHEN you encounter a method that converts a **numeric primitive wrapper type** (Integer, Long, Short, Float, Double) to a `java.nio.ByteBuffer` using the pattern: allocate N bytes → putValue(value) → flip() → return buffer

THEN you MUST write an explicit test that:
1. Calls the conversion method to obtain a ByteBuffer
2. Calls the corresponding `buffer.getXxx()` method (e.g., `buffer.getInt()` for Integer, `buffer.getLong()` for Long, `buffer.getDouble()` for Double, `buffer.getFloat()` for Float, `buffer.getShort()` for Short) on the returned buffer
3. Asserts that the retrieved value matches the original input value
4. Specifically verify that NO `BufferUnderflowException` is thrown during the `getXxx()` call

**Common pitfalls to avoid:**
- Testing only that the ByteBuffer is non-null — this does NOT verify the correct position/limit state of the buffer after flip
- Forgetting to call `getXxx()` at all — a `.flip()` bug may not manifest until the buffer is actually read
- Testing with a String and a charset rather than testing the numeric primitive overloads
- Assuming that `ByteBuffer.allocate(N).putXxx(v).flip()` always produces a readable buffer — position handling errors in `.flip()` can leave the buffer in an unreadable state
- Only testing `toByteArray()`/`toString()` conversions that use `ByteBuffer.wrap()` while ignoring the allocate+put+flip overloads

**Correct example (for Integer):**
```java
public void testToByteBufferInteger() {
    ByteBuffer bb = NIOConverter.toByteBuffer(Integer.valueOf("2"));
    assertNotNull(bb);
    // This calls getInt() which must NOT throw BufferUnderflowException
    assertEquals(2, bb.getInt());
}
```

**Correct example (for Long):**
```java
public void testToByteBufferLong() {
    ByteBuffer bb = NIOConverter.toByteBuffer(Long.valueOf("2"));
    assertNotNull(bb);
    assertEquals(2L, bb.getLong());
}
```

**Incorrect example (will miss the bug):**
```java
public void testToByteBufferInteger() {
    ByteBuffer bb = NIOConverter.toByteBuffer(Integer.valueOf("2"));
    assertNotNull(bb);
    // Missing: bb.getInt() — buffer might have wrong position/limit
    // and the test would pass even on the buggy version
}
```

**Why this matters:** When `toByteBuffer(Integer)` uses `ByteBuffer.allocate(4); buf.putInt(value); buf.flip();`, a bug in the implementation (e.g., using `.flip()` on an already-flipped buffer or using the wrong allocation size) can leave the buffer's position at the end, causing a `BufferUnderflowException` when `getInt()` is called. The test must read the value back from the buffer to verify the buffer is in a correct readable state.