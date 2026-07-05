---
name: serialization-pattern-testing
description: When testing classes that implement Serializable, verify the serialization
  round-trip preserves all fields and does not throw exceptions. This skill helps
  catch bugs where serialized objects fail to deserialize correctly due to missing
  writeObject/readObject consistency, transient field issues, or improper serialVersionUID.
code_tags:
- SERIALIZATION_HANDLING
test_pattern: STATE_TEST
---

# serialization-pattern-testing

## Instructions

# Serialization Round-Trip Testing

## Instructions

- WHEN the TG encounters a class that implements `java.io.Serializable`
- THEN it should write a test that:
  1. Creates an instance of the class with realistic field values
  2. Serializes the instance to a byte array using `ObjectOutputStream`
  3. Deserializes it back using `ObjectInputStream`
  4. Asserts that the deserialized object is not null and equals the original
  5. Catches and asserts NO exception occurs during the full round-trip (using `assertDoesNotThrow` or `fail()` in catch blocks)

- WHEN the class has transient fields, custom `writeObject()`/`readObject()` methods, or relies on reflective state (e.g., proxy templates with `CtTypeReference` fields)
- THEN the test should specifically verify that:
  - All non-transient fields are correctly restored after deserialization
  - Custom serialization methods do not throw `IOException` or `ClassNotFoundException`
  - The deserialized object can be used without throwing `NullPointerException` or `ClassCastException`

- Common pitfalls to avoid:
  - Testing only construction or method calls without verifying serialization round-trip works
  - Assuming serialization works because the class implements Serializable
  - Forgetting to test with non-trivial object types (e.g., `CtTypeReference`, `CtBlock`) instead of only strings or primitives
  - Not using `ByteArrayOutputStream`/`ByteArrayInputStream` for in-memory round-trip testing
  - Testing serialization but not verifying the deserialized object's usability (e.g., calling methods on it)

- Example of a correct test pattern:

```java
// Good: validates full serialization round-trip
@Test
public void testSerializationRoundTrip() {
    // Arrange
    MySerializableClass original = new MySerializableClass();
    original.setSomeField("testValue");
    // Act & Assert
    assertDoesNotThrow(() -> {
        ByteArrayOutputStream bos = new ByteArrayOutputStream();
        ObjectOutputStream oos = new ObjectOutputStream(bos);
        oos.writeObject(original);
        oos.flush();
        ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
        ObjectInputStream ois = new ObjectInputStream(bis);
        MySerializableClass deserialized = (MySerializableClass) ois.readObject();
        // Assert
        assertNotNull(deserialized);
        assertEquals("testValue", deserialized.getSomeField());
    });
}
```

- Example of an incorrect test pattern:

```java
// Bad: only tests construction, no serialization verification
@Test
public void testConstruction() {
    MySerializableClass obj = new MySerializableClass();
    obj.setSomeField("testValue");
    // Never verifies serialization works!
}
```