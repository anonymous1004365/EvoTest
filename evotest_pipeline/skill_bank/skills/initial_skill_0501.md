---
name: pojo-serializer-sequence-reuse-corruption
description: Tests PojoSerializers whose copy(DataInputView, DataOutputView) method
  may corrupt internal state (e.g., subclassSerializerCache) when deserializing non-registered
  subclass instances in sequence without allocating fresh intermediate objects. When
  the serializer reuses internal buffers/state across a sequence of copy operations,
  subsequent deserializations can produce corrupted or null field values.
code_tags:
- STATE_MUTATION
- NULL_CHECK
- SERIALIZER_REUSE_CORRUPTION
test_pattern: PARAMETRIC_TEST
---

# pojo-serializer-sequence-reuse-corruption

## Instructions

# Pojo Serializer Sequence Reuse Corruption

## Instructions

### WHEN
The Test Generator encounters a `PojoSerializer` (or similar TypeSerializer) that:

1. Has a `subclassSerializerCache` (a `HashMap<Class<?>, TypeSerializer<?>>`) used to cache non-registered subclass serializers on-the-fly.
2. Has a `copy(DataInputView source, DataOutputView target)` method that reads and writes subclass instances by:
   - First reading subclass metadata (header flags, class tags, etc.)
   - Then using a **reused/recycled** intermediate object (e.g., from a local `ByteArrayOutputStreamWithPos` or `DataOutputViewStreamWrapper` pattern) to convert the subclass instance to bytes before writing to the target.
3. The `copy()` method does not **guarantee a fresh temporary buffer** for each serialized field/subclass — instead it reuses a mutable intermediate object whose internal state (position, buffer) may carry over data from a previous subclass serialization.

### THEN
The TG must write a **sequence reuse test** that:

1. Creates a serializer instance for the base POJO class (e.g., `PojoSerializer<SimplePojo>`).
2. Creates **two different subclass instances** — one that IS a direct instance of the base class, and one that IS a **non-registered subclass** (a class that extends the base class but is NOT registered in the execution config).
3. Serializes the first (non-subclass) instance via `serialize(value, out)`.
4. Serializes the second (subclass) instance via `serialize(value, out)`.
5. Calls `copy(source, target)` to copy the **entire serialized sequence** from one `DataInputView` to a `DataOutputView`.
6. Re-reads both values from the **target** and verifies each is **deep-equal** to its original.
7. Specifically checks that **the non-registered subclass instance** is not corrupted (no null fields, correct values).

**Importantly**, this test must use a **reusing deserialize pattern**: `serializer.deserialize(reuseInstance, source)` where `reuseInstance` is the **same** instance across multiple deserialization calls.

### Concrete Implementation Steps

- **Test data**: Include at least:
  - One instance that is exactly the base POJO class (e.g., `new SimplePojo(42, "hello")`)
  - One instance that is a **non-registered subclass** of the base POJO (e.g., `new SimplePojoSubclass(99, "world", 3.14)` where `SimplePojoSubclass` extends `SimplePojo` but is NOT in the registered subclasses)

- **Serialization**: Write all test data to a `ByteArrayOutputStream` using a `DataOutputViewStreamWrapper`.

- **Copy**: Read from the serialized bytes and write to a new `ByteArrayOutputStream` using `serializer.copy(inputView, outputView)`.

- **Deserialize with reuse**: Create a single `T reuse = serializer.createInstance()`. Then for each copied value, deserialize via `serializer.deserialize(reuse, inputCopy)` and verify it equals the original.

- **Validation**: Use `assertEquals(original, deserialized)` after calling `.toString()` on the deserialized value (as per the `SerializerTestBase` convention). Also assert that subclass-specific fields are not null (e.g., `assertNotNull(((SimplePojoSubclass)deserialized).getExtraField())`).

### Common Pitfalls to Avoid

- ❌ **Testing only base class instances**: If you test only `SimplePojo` instances, the `subclassSerializerCache` is never exercised and the corruption remains hidden.
- ❌ **Testing registered subclasses only**: Registered subclass serializers are pre-allocated and stable; only **non-registered** subclasses trigger the on-the-fly caching that can be corrupted.
- ❌ **Using fresh instances for each deserialization**: The bug manifests only when the **same** reuse target is used for consecutive deserializations of non-registered subclass instances, because the internal `subclassSerializerCache` produces incorrect results when the intermediate write buffer is not reset.
- ❌ **Forgetting `.toString()`**: The `SerializerTestBase` pattern calls `.toString()` on deserialized values; this is important for detecting internal corruption in certain serializer types (like Kryo), but for Pojo serializers the deep equality check is the primary validation.

### Correct Example

```java
// Test that catches the corruption bug
@Test
public void testSerializeAsSequenceReusingValues() {
    TypeSerializer<SimplePojo> serializer = createSerializer();
    SimplePojo[] testData = getTestData(); // includes both SimplePojo and SimplePojoSubclass
    
    // Serialize all values to a single stream
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    DataOutputViewStreamWrapper out = new DataOutputViewStreamWrapper(baos);
    for (SimplePojo value : testData) {
        serializer.serialize(value, out);
    }
    
    // Copy the entire sequence
    ByteArrayOutputStream baosCopy = new ByteArrayOutputStream();
    DataOutputViewStreamWrapper target = new DataOutputViewStreamWrapper(baosCopy);
    serializer.copy(
        new DataInputViewStreamWrapper(new ByteArrayInputStream(baos.toByteArray())),
        target
    );
    
    // Deserialize with reuse
    SimplePojo reuse = serializer.createInstance();
    DataInputViewStreamWrapper source = 
        new DataInputViewStreamWrapper(new ByteArrayInputStream(baosCopy.toByteArray()));
    for (SimplePojo value : testData) {
        SimplePojo deserialized = serializer.deserialize(reuse, source);
        assertEquals(value + "", deserialized + ""); // toString
        assertEquals(value, deserialized);
        reuse = deserialized;
    }
}
```

### Incorrect Example

```java
// ❌ BAD: Only tests base class, no copy between serialize/deserialize
@Test
public void testSimpleSerialization() {
    TypeSerializer<SimplePojo> serializer = createSerializer();
    SimplePojo value = new SimplePojo(42, "hello"); // only base class
    
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    serializer.serialize(value, new DataOutputViewStreamWrapper(baos));
    
    SimplePojo result = serializer.deserialize(
        serializer.createInstance(),
        new DataInputViewStreamWrapper(new ByteArrayInputStream(baos.toByteArray()))
    );
    assertEquals(value, result); // passes even with the bug
}
```