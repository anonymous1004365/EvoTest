---
name: kryo-output-buffer-clear-on-exception
description: WHEN a Kryo serializer catches a KryoException whose cause is EOFException
  (signaling buffer full), THEN the test must verify that output.clear() is called
  so the output buffer is reset to position 0, enabling subsequent serialization to
  proceed without stale data.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- BUFFER_OFFSET_HANDLING
- EXCEPTION_HANDLING
- STATE_MUTATION
test_pattern: STATE_TEST
---

# kryo-output-buffer-clear-on-exception

## Instructions

# Kryo Output Buffer Must Be Cleared on Exception

## Instructions

- WHEN the TG encounters code that uses a `com.esotericsoftware.kryo.io.Output` buffer within a `serialize()` method that catches a `KryoException` whose cause is `EOFException` (denoting a full buffer),
- THEN the TG must write a test that:
  1. Creates a custom `DataOutputView` whose `checkSize(int numBytes)` method throws `EOFException` when `position + numBytes > buffer.length`.
  2. Uses a `TestRecord` with a fixed-size `byte[]` field and a custom `Serializer<TestRecord>` that writes `object.buffer.length` (int) then `object.buffer` (bytes).
  3. Registers both the `TestRecord` type and its custom serializer via `executionConfig.registerTypeWithKryoSerializer(TestRecord.class, new TestRecordSerializer())` and `executionConfig.registerKryoType(TestRecord.class)`.
  4. Creates a `KryoSerializer<TestRecord>` with a target buffer that is too small to hold two records (e.g., bufferSize=150 when single record serialization size is 100).
  5. Calls `kryoSerializer.serialize(testRecord, target)` — this should succeed once.
  6. Calls `kryoSerializer.serialize(testRecord, target)` again — this MUST throw `EOFException`.
  7. After catching the `EOFException`, verifies that the first record can still be deserialized correctly from the target buffer.
  8. Clears the target buffer, then calls `kryoSerializer.serialize(testRecord, target)` again — this must succeed, proving that the internal Kryo `Output` buffer was cleared (position reset to 0) during the exception handling.

- WHEN verifying the buffer was cleared, the test should:
  - Assert that after the EOFException, the first record CAN be deserialized (via `kryoSerializer.deserialize(new DataInputViewStreamWrapper(new ByteArrayInputStream(target.getBuffer())))`) and equals the original record.
  - Assert that after clearing the target and serializing again, the buffer contains exactly the expected number of marker bytes (e.g., 42 bytes if the record's buffer was filled with `(byte)42`).

- Common pitfalls to avoid:
  - ❌ Testing only the happy path (no buffer-full scenario). The bug manifests specifically when `EOFException` is thrown mid-serialization.
  - ❌ Re-creating the `KryoSerializer` or `Output` between the two serialize calls. The reuse of the same `Output` instance is essential to trigger the stale-position bug.
  - ❌ Not registering the custom serializer via `registerTypeWithKryoSerializer` — the test will use Kryo's default serializer instead, which may not trigger the exact write path.
  - ❌ Using a buffer large enough to hold two records — the buffer must be just large enough for ONE record but NOT for two, so the second `serialize()` call overflows and throws `EOFException`.
  - ❌ Forgetting that `output.clear()` resets the Kryo `Output`'s `position()` but does NOT clear the underlying `DataOutputViewStream`. The test must explicitly clear the target buffer when testing subsequent serialization.

### Correct Example

```java
@Test
public void testOutputBufferedBeingClearedInCaseOfException() throws Exception {
    ExecutionConfig executionConfig = new ExecutionConfig();
    executionConfig.registerTypeWithKryoSerializer(TestRecord.class, new TestRecordSerializer());
    executionConfig.registerKryoType(TestRecord.class);

    KryoSerializer<TestRecord> kryoSerializer = new KryoSerializer<>(TestRecord.class, executionConfig);

    int size = 94;
    int bufferSize = 150;
    TestRecord testRecord = new TestRecord(size);
    TestDataOutputView target = new TestDataOutputView(bufferSize);

    // First serialize succeeds
    kryoSerializer.serialize(testRecord, target);

    // Second serialize overflows the buffer -> EOFException
    try {
        kryoSerializer.serialize(testRecord, target);
        fail("Expected EOFException");
    } catch (EOFException e) {
        // Expected — Kryo Output buffer must have been cleared in the catch block
    }

    // First record is still recoverable from target
    TestRecord actual = kryoSerializer.deserialize(
        new DataInputViewStreamWrapper(new ByteArrayInputStream(target.getBuffer())));
    assertEquals(testRecord, actual);

    // Clear target and re-serialize: should succeed only if Output was cleared
    target.clear();
    kryoSerializer.serialize(testRecord, target);
    // Verify data integrity
    int counter = 0;
    for (byte b : target.getBuffer()) { if (b == 42) counter++; }
    assertEquals(size, counter);
}
```

### Incorrect Example

```java
@Test
public void testBadExample() throws Exception {
    ExecutionConfig executionConfig = new ExecutionConfig();
    // ❌ Missing registration of custom serializer
    KryoSerializer<TestRecord> kryoSerializer = new KryoSerializer<>(TestRecord.class, executionConfig);

    int bufferSize = 1000; // ❌ Too large — won't trigger buffer full
    TestRecord testRecord = new TestRecord(50);
    TestDataOutputView target = new TestDataOutputView(bufferSize);

    kryoSerializer.serialize(testRecord, target); // happy path only
    kryoSerializer.serialize(testRecord, target); // succeeds silently, but doesn't test the fix
}
```