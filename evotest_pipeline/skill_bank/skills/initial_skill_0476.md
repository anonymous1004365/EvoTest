---
name: null-check-on-bytebuffer-constructor
description: When a class constructor accepts a ByteBuffer, the constructor must explicitly
  null-check the ByteBuffer parameter before calling methods like ByteBufferUtil.toBytes(ByteBuffer),
  which internally calls buffer.array(), buffer.limit(), and buffer.position() — all
  of which throw NullPointerException on a null ByteBuffer.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# null-check-on-bytebuffer-constructor

## Instructions

# Null Check on ByteBuffer Constructor Parameter

## Instructions

- WHEN the TG encounters a class constructor that accepts a `java.nio.ByteBuffer` parameter (e.g., `Value(ByteBuffer src)`), and that constructor passes the ByteBuffer to a utility method (e.g., `ByteBufferUtil.toBytes(ByteBuffer)`) which internally calls `buffer.array()`, `buffer.limit()`, or `buffer.position()`,
- THEN the TG should write an exception test that passes `null` as the ByteBuffer argument and asserts `NullPointerException` is thrown.
- The test should verify that the constructor explicitly validates its ByteBuffer argument for null before any dereference, not relying on downstream methods.

### Common pitfalls to avoid:
- Testing only with non-null ByteBuffer values and missing the null-ByteBuffer edge case entirely.
- Assuming that passing null to a downstream utility method will produce a clear error — without a null check in the constructor, the error will be a cryptic `NullPointerException` from inside `ByteBuffer.array()` or similar, not from the constructor itself.
- Writing a test that asserts an exception type other than `NullPointerException` — the expected exception must be `NullPointerException`.

### Correct test example (JUnit 4):
```java
@Test(expected = NullPointerException.class)
public void testNullByteBufferConstructor() {
    new Value((java.nio.ByteBuffer) null);
}
```

### Incorrect test example (missing the null check scenario):
```java
@Test
public void testByteBufferConstructor() {
    byte[] data = "hello".getBytes();
    java.nio.ByteBuffer buf = java.nio.ByteBuffer.wrap(data);
    Value v = new Value(buf);
    assertArrayEquals(data, v.get());
    // Fails to test the null ByteBuffer case
}
```