---
name: bytebuffer-type-conversion-detection
description: ''
code_tags:
- CACHING_AND_CONVERTER_REGISTRY
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# bytebuffer-type-conversion-detection

## Instructions

# ByteBuffer Type Conversion Detection

## Instructions

- WHEN the TG encounters a type converter method that accepts a `java.nio.ByteBuffer` parameter (e.g., `toStreamSource(ByteBuffer buffer)`)
- THEN the TG must write an EXCEPTION_TEST verifying that BOTH heap buffers (with backing arrays) AND direct buffers (no backing arrays) are handled correctly:
  - First, write a test with a heap `ByteBuffer` created via `ByteBuffer.allocate(int)` — this has a backing array
  - Second, write a test with a direct `ByteBuffer` created via `ByteBuffer.allocateDirect(int)` — this does NOT have a backing array
  - The test should verify that the conversion succeeds for both buffer types without throwing `UnsupportedOperationException`
  - Additionally, verify the conversion output is semantically correct (e.g., the StreamSource is not null and produces expected content)

- Common pitfall: Testing only with `ByteBuffer.allocate()` (heap buffers) and assuming all ByteBuffers behave the same. Direct buffers (`allocateDirect`) do not have backing arrays, so calling `buffer.array()` on them throws `UnsupportedOperationException`. The converter must guard against this with `buffer.hasArray()` checks.

- Correct example:
```java
@Test
public void testToStreamSourceWithDirectByteBuffer() throws Exception {
    ByteBuffer directBuf = ByteBuffer.allocateDirect(64);
    directBuf.put("hello".getBytes());
    directBuf.flip();
    StreamSource source = converter.toStreamSource(directBuf);
    assertNotNull(source);
    // verify content...
}
```

- Incorrect example (only tests heap buffers):
```java
@Test
public void testToStreamSource() throws Exception {
    ByteBuffer heapBuf = ByteBuffer.allocate(64);
    heapBuf.put("hello".getBytes());
    heapBuf.flip();
    StreamSource source = converter.toStreamSource(heapBuf);
    assertNotNull(source);
    // Missing: direct buffer test!
}
```