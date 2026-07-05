---
name: writable-serialization-roundtrip-verify
description: WHEN testing Writable implementations that have complex state (collections,
  nested objects), THEN use serialization roundtrip tests to verify all fields are
  properly serialized and deserialized. Prevents bugs where fields are set but never
  written to DataOutput or never read back from DataInput.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
- NULL_CHECK
- SERIALIZATION_PERSISTENCE
test_pattern: STATE_TEST
---

# writable-serialization-roundtrip-verify

## Instructions

# Writable Serialization Roundtrip Verification

## Instructions

WHEN the TG encounters a class implementing `org.apache.hadoop.io.Writable` (with `readFields(DataInput)` and `write(DataOutput)` methods) that has multiple optional/custom fields (especially collections like `List`, `Set`, maps, or custom objects), THEN the TG should write a roundtrip serialization test that:

1. Create an instance of the Writable class and populate ALL of its fields with non-default values, including:
   - Collections (e.g., `List<IteratorSetting>`, `Set<Pair<Text,Text>>`)
   - Nested Writable objects (e.g., `IteratorSetting` which itself implements Writable)
   - Primitive wrappers (`Boolean`, `Integer`, etc.)
   - Enum types
   - Custom domain objects

2. Serialize the object to a `ByteArrayOutputStream` via `DataOutputStream`, then deserialize into a NEW instance via `ByteArrayInputStream`/`DataInputStream`.

3. Assert that every field value on the deserialized object equals the original field value. Use `Assert.assertEquals` for each field individually, NOT just `Assert.assertEquals(original, deserialized)` on the whole object.

4. Common pitfalls to avoid:
   - ❌ Testing only simple fields (range, locations, table name) while missing complex fields (iterators, fetched columns, auths, token, log level, sampler config)
   - ❌ Forgetting that `readFields` may use conditional presence flags (`in.readBoolean()` before reading a field), meaning the test MUST set the field to a non-null value to exercise that code path
   - ❌ Assuming that because `setIterators(...)` was called, the iterators list will survive serialization — the `write()` method might not include that field if the conditional check is missing or wrong
   - ❌ Using only empty collections or null values — the test must use non-empty collections with configured elements

5. Correct test pattern example:

```java
// Arrange: create object and populate ALL fields
MyWritable original = new MyWritable();
original.setField1("value1");
original.setField2(42);
List<SomeWritable> items = new ArrayList<>();
items.add(new SomeWritable("config1"));
items.add(new SomeWritable("config2"));
original.setItems(items);

// Act: serialize then deserialize
ByteArrayOutputStream baos = new ByteArrayOutputStream();
DataOutputStream dos = new DataOutputStream(baos);
original.write(dos);

MyWritable deserialized = new MyWritable();
ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
DataInputStream dis = new DataInputStream(bais);
deserialized.readFields(dis);

// Assert: verify ALL fields
Assert.assertEquals(original.getField1(), deserialized.getField1());
Assert.assertEquals(original.getField2(), deserialized.getField2());
Assert.assertEquals(original.getItems(), deserialized.getItems());
```

6. Incorrect test pattern (would miss the bug):

```java
// ❌ Only tests basic fields, misses complex ones
MyWritable original = new MyWritable();
original.setField1("value1");
// Never sets or verifies getItems()!

ByteArrayOutputStream baos = new ByteArrayOutputStream();
// ... serialize and deserialize ...

Assert.assertEquals(original.getField1(), deserialized.getField1());
// Missing: Assert.assertEquals(original.getItems(), deserialized.getItems());
```