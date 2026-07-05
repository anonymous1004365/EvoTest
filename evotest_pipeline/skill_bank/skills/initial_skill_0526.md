---
name: writable-serialization-roundtrip
description: Teaches how to test Writable serialization round-trips for classes implementing
  Hadoop Writable, where write/readFields must handle all fields in consistent order
  and type. Apply when a class implements Writable and has boolean or collection fields.
code_tags:
- STATE_MUTATION
- SERIALIZATION_ROUNDTRIP
test_pattern: STATE_TEST
---

# writable-serialization-roundtrip

## Instructions

# Writable Serialization Round-Trip Testing

## Instructions

- WHEN the code under test implements `org.apache.hadoop.io.Writable` (interface with `write(DataOutput)` and `readFields(DataInput)`) AND has multiple boolean fields or collection/object reference fields that can be null
- THEN write a round-trip serialization test that:
  1. Creates an instance of the class
  2. Sets multiple boolean fields to values that differ from their defaults (e.g. set `autoAdjustRanges=false`, `offlineScan=true`, `useIsolatedScanners=true`, `useLocalIterators=true`)
  3. Serializes the object via `write(DataOutputStream)` to a `ByteArrayOutputStream`
  4. Deserializes a new instance via `readFields(DataInputStream)` from the resulting `ByteArrayInputStream`
  5. Asserts `assertEquals(originalObject, deserializedObject)` to verify all fields survive the round-trip
  6. Tests that Boolean fields are written/read in a consistent order and that default values are handled correctly

- Common pitfalls to avoid:
  - **Testing only the default (no-arg constructed) object**: A default object where all booleans are `false` and collections are `null` may pass even if the serialization code has a mismatch bug (e.g., writing fields in wrong order or skipping a field). The bug manifests only when a non-default configuration is used.
  - **Testing only collection fields without testing boolean fields**: The bug may be in boolean field ordering (write order ≠ read order), so test both boolean and collection fields separately AND together.
  - **Relying only on `equals()` between original and deserialized objects**: If `equals()` is not properly implemented, the test may produce false negatives/positives. Verify `equals()` coverage or check individual getter values as well.
  - **Using same stream for multiple serializations**: Always create fresh `ByteArrayOutputStream` and `DataOutputStream` per serialization test.

- Correct approach:
```java
// Good: Tests non-default boolean values for all boolean flags
@Test
public void testSerialization_allBooleans() throws IOException {
    InputTableConfig config = new InputTableConfig();
    config.setAutoAdjustRanges(false);     // default: true
    config.setOfflineScan(true);            // default: false
    config.setUseIsolatedScanners(true);    // default: false
    config.setUseLocalIterators(true);      // default: false

    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    config.write(new DataOutputStream(baos));
    baos.close();

    InputTableConfig actual = new InputTableConfig(new DataInputStream(new ByteArrayInputStream(baos.toByteArray())));

    assertEquals(config, actual);
    // Also verify individual booleans to catch equals() issues
    assertFalse(actual.shouldAutoAdjustRanges());
    assertTrue(actual.isOfflineScan());
    assertTrue(actual.shouldUseIsolatedScanners());
    assertTrue(actual.shouldUseLocalIterators());
}
```

- Incorrect approach (will NOT catch this bug):
```java
// Bad: Only tests default (all-false) boolean values
@Test
public void testSerialization_default() throws IOException {
    InputTableConfig config = new InputTableConfig(); // all false booleans
    // serialize and deserialize...
    assertEquals(config, actual);
    // Passes even when write order is wrong because both sides
    // read the same wrong boolean value (false for each)
}
```