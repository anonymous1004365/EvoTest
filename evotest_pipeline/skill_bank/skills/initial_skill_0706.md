---
name: kryo-deserialization-eof-forwarding
description: When testing deserialization of truncated/incomplete Kryo serialized
  data, ensure that the underlying java.io.EOFException from the input stream is properly
  forwarded (not wrapped in a KryoException). This skill helps catch bugs where Kryo's
  deserialization catches and re-wraps the EOFException instead of letting it propagate.
code_tags:
- EXCEPTION_HANDLING
- RESOURCE_MANAGEMENT
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# kryo-deserialization-eof-forwarding

## Instructions

# Kryo Deserialization EOF Exception Forwarding

## Instructions

### WHEN the TG encounters:
- A Kryo serializer's `deserialize(DataInputView)` method that reads from an input stream backed by limited/truncated data
- The deserialization wraps the read in a Kryo `Input` and calls Kryo's `readClassAndObject()` or similar method
- An `EOFException` could be thrown by the underlying `DataInputView` when the stream ends prematurely

### THEN the TG should:
1. **Create a test that truncates or limits the input data** so that deserialization will hit the end of the stream before fully reading an object.
2. **Expect `java.io.EOFException` to be thrown** (unwrapped) — NOT a `com.esotericsoftware.kryo.KryoException`.
3. **Use a real serialized object** (e.g., serialize a known object, then truncate its byte array) to ensure the path through Kryo's internal deserialization is exercised.
4. **Assert with `assertThrows(java.io.EOFException.class, ...)`** to verify the exact exception type is preserved.

### Concrete example (correct):
```java
@Test
public void testForwardEOFExceptionWhileDeserializing() {
    // Serialize a known object first
    SomeType original = new SomeType("test", 42);
    byte[] serialized = serializer.serialize(original);
    
    // Truncate the serialized data to simulate stream ending prematurely
    byte[] truncated = Arrays.copyOf(serialized, serialized.length / 2);
    
    // Deserialization should throw EOFException, not KryoException
    assertThrows(
        java.io.EOFException.class,
        () -> serializer.deserialize(new ByteArrayInputStreamView(truncated)),
        "Deserializing truncated Kryo data should throw EOFException"
    );
}
```

### Common pitfalls to avoid:
- ❌ **Testing with `KryoException` or generic `Exception`** — the bug is that the wrong exception type is thrown; only `EOFException` proves the fix works.
- ❌ **Using a completely empty byte array** — this may throw a different exception earlier in the pipeline (e.g., buffer underflow) rather than exercising the Kryo deserialization path where the bug lives.
- ❌ **Only testing with String types** — the bug manifests when deserializing any type through Kryo's generic serializer path; test with complex types that exercise Kryo's internal reading.
- ❌ **Checking the exception message** instead of the type — the fix is about preserving the exception **type**, not the message content.
- ❌ **Mocking the input stream** — the bug requires real Kryo deserialization flow through the `Input` class; mocks won't reproduce the issue.