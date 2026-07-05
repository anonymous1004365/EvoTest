---
name: kryo-reference-mapping-validation
description: When testing Kryo serializers that use reference-based serialization,
  verify that enabling Kryo references does not cause serialization failures. This
  skill applies when the serializer's Kryo instance has references enabled (kryo.setReferences(true))
  and the test must validate that serialization works correctly with generic types.
code_tags:
- KRYO_REFERENCES_ENABLED
test_pattern: EXCEPTION_TEST
---

# kryo-reference-mapping-validation

## Instructions

# Kryo Reference Mapping Validation

## Instructions

WHEN the code under test creates or configures a Kryo serializer instance where `kryo.setReferences(true)` is called (Kryo references enabled), AND the serializer handles generic types or complex object graphs:

- THEN create a test that serializes and deserializes an object containing the generic type being registered, and verify that no `NullPointerException` or `IllegalArgumentException` is thrown during serialization.
- Specifically, construct an instance of the type being serialized (e.g., a generic container like `Tuple2<String, SomeType>`), serialize it with the Kryo serializer, and deserialize it back. Assert that the round-trip succeeds.
- Additionally, obtain the underlying Kryo instance (via a `getKryo()` method if available) and verify that registration IDs for types are positive integers (`> 0`), confirming proper registration.
- **Common pitfall**: Only testing with a simple type (e.g., `String` or `Integer`) may not trigger the bug. The bug manifests when the generic type parameter of the serializer is a non-trivial class (e.g., `Path.class`, `File.class`, or a custom class with complex object graphs). Always test with the actual generic type that the serializer is instantiated with.
- **Expected failure on buggy version**: When Kryo references are enabled, serialization of certain generic types may throw `NullPointerException` because the reference resolver is not properly initialized for generic type mappings. The test should expect this exception on the buggy version and verify no exception on the fixed version.
- **What to assert**: Use `assertDoesNotThrow()` (JUnit 5) or `try-catch` with `Assert.fail()` pattern to verify the serialization round-trip completes without error. Also assert `assertTrue(serializer.getKryo().getRegistration(SomeType.class).getId() > 0)` to confirm proper Kryo registration.

### Correct Example (What the TG should do)

```java
@Test
public void validateReferenceMappingEnabled() {
    // Create serializer with generic type that triggers the bug
    TypeSerializer<Tuple2<String, Path>> serializer = TypeInformation.of(
        new TypeHint<Tuple2<String, Path>>() {}).createSerializer(new ExecutionConfig());
    
    // Get the underlying Kryo instance and verify references are enabled
    Kryo kryo = ((KryoSerializer<?>) serializer).getKryo();
    assertTrue(kryo.getReferences());  // references must be enabled
    
    // Create an instance to serialize
    Tuple2<String, Path> instance = new Tuple2<>("/tmp/test", new Path("/some/path"));
    
    // Serialize and deserialize - should not throw on fixed version
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    DataOutputViewStreamWrapper out = new DataOutputViewStreamWrapper(baos);
    assertDoesNotThrow(() -> serializer.serialize(instance, out));
    
    // Verify registration
    assertTrue(kryo.getRegistration(Path.class).getId() > 0);
}
```

### Incorrect Example (What the TG should NOT do)

```java
// BAD: Only tests with String type - doesn't trigger reference mapping issue
@Test
public void testSerialization() {
    TypeSerializer<String> serializer = TypeInformation.of(String.class)
        .createSerializer(new ExecutionConfig());
    
    // This test passes even on buggy version - misses the bug entirely
    String value = "test";
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    DataOutputViewStreamWrapper out = new DataOutputViewStreamWrapper(baos);
    serializer.serialize(value, out);  // no exception thrown even on buggy version
}
```