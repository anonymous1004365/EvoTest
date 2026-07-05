---
name: bytebuffer-nonzero-offset-testing
description: When a utility method accepts a ByteBuffer and accesses it via hasArray()
  path, tests must cover ByteBuffers with non-zero arrayOffset() — created via ByteBuffer.slice()
  — to catch incorrect offset calculations. Without this, methods may silently extract
  wrong data despite passing with zero-offset buffers.
code_tags:
- BUFFER_OFFSET_HANDLING
test_pattern: PARAMETRIC_TEST
---

# bytebuffer-nonzero-offset-testing

## Instructions

# ByteBuffer Non-zero Array Offset Testing

## Instructions

- WHEN the TG encounters a method that handles `ByteBuffer` objects and uses `buffer.hasArray()` to branch logic (accessing `buffer.array()` with `buffer.arrayOffset()`, `buffer.position()`, or `buffer.limit()`)
- THEN the TG MUST write a test that creates a `ByteBuffer` with a **non-zero array offset** by wrapping a larger backing array and calling `slice()`, and verify the method returns the correct data. Specifically:
  - Create a byte array like `"0123456789".getBytes(UTF_8)`
  - Call `ByteBuffer.wrap(data, 3, 4)` to get a view with position=3, limit=7
  - Call `.slice()` on it to produce a ByteBuffer with `arrayOffset()=3`, `position()=0`, `remaining()=4`
  - Verify the method under test returns `"3456"` (the correct content), not `"0123"` (content from offset 0)
- ALSO test with non-zero position in addition to non-zero array offset: call `.get()` on the sliced buffer to advance position, then verify the method returns `"456"`
- ALSO test with buffers that have zero array offset but non-zero position (`ByteBuffer.wrap(data, 3, 4)` directly, without slice), and with zero offset and zero position
- ALSO test with `ByteBuffer.allocateDirect()` (no backing array) to cover the else branch

- **Common pitfall**: Testing only with `ByteBuffer.wrap(data)` or `ByteBuffer.wrap(data, 0, data.length)` which produces a zero array offset. This misses the bug entirely because the buggy code incorrectly computes the offset — tests that only use zero-offset buffers will pass on both buggy and fixed code.
- **Common pitfall**: Incorrectly using `buffer.arrayOffset()` without adding `buffer.position()` when the buffer has a non-zero array offset — both must be combined to get the correct starting index in the backing array.

### Correct example (catches the bug):
```java
byte[] data = "0123456789".getBytes(UTF_8);
ByteBuffer bb1 = ByteBuffer.wrap(data, 3, 4);
ByteBuffer bb2 = bb1.slice();  // arrayOffset()=3, position()=0, limit()=4
// Verify method returns "3456" not "0123"
byte[] result = ByteBufferUtil.toBytes(bb2);
Assert.assertEquals("3456", new String(result, UTF_8));
```

### Incorrect example (misses the bug):
```java
byte[] data = "0123456789".getBytes(UTF_8);
ByteBuffer bb = ByteBuffer.wrap(data, 0, 4);  // arrayOffset()=0
byte[] result = ByteBufferUtil.toBytes(bb);
Assert.assertEquals("0123", new String(result, UTF_8));  // passes even with bug
```