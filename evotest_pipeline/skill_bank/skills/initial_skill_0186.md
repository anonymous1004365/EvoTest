---
name: kryo-serializer-reference-mapping-configuration
description: WHEN testing KryoSerializer configuration, THEN verify that Kryo reference
  mapping is properly initialized by checking kryo.getReferences() returns true. This
  skill helps catch bugs where the Kryo instance is initialized without setting setReferences(true),
  which causes failures for serializers that depend on object reference tracking.
code_tags:
- STATE_MUTATION
test_pattern: STATE_TEST
---

# kryo-serializer-reference-mapping-configuration

## Instructions

# Kryo Serializer Reference Mapping Configuration

## Instructions

WHEN the TG encounters a serializer class (like `KryoSerializer`) that lazily initializes a Kryo instance via a method like `getKryoInstance()` or `ensureKryoInitialized()`, and this Kryo instance is configured with `setRegistrationRequired(false)`, `setInstantiatorStrategy(...)`, etc., THEN the TG should verify that `kryo.setReferences(true)` is also called during initialization.

Specifically:
- The test should create a `KryoSerializer` instance (e.g., `new KryoSerializer<>(String.class, new ExecutionConfig())`)
- Call `serializer.getKryo()` to force lazy initialization of the Kryo instance
- Assert that `kryo.getReferences()` returns `true` (i.e., `assertTrue(kryo.getReferences())`)
- The test should be in a dedicated test method like `validateReferenceMappingEnabled()`

Common pitfalls to avoid:
- Testing only serialization/deserialization round-trips without checking the underlying Kryo configuration
- Assuming that the default Kryo configuration includes reference mapping (Kryo's default is `setReferences(true)`, but it must be explicitly set when using a custom initialization method)
- Only testing with simple types like `String` or `Integer` — the reference mapping is critical for cyclic object graphs and shared object references
- Testing the config snapshot/restore without verifying the actual Kryo instance state

### Correct example:
```java
@Test
public void validateReferenceMappingEnabled() {
    KryoSerializer<String> serializer = new KryoSerializer<>(String.class, new ExecutionConfig());
    Kryo kryo = serializer.getKryo();
    assertTrue("Kryo reference mapping must be enabled", kryo.getReferences());
}
```

### Incorrect example (missing the check):
```java
@Test
public void validateReferenceMappingEnabled() {
    KryoSerializer<String> serializer = new KryoSerializer<>(String.class, new ExecutionConfig());
    Kryo kryo = serializer.getKryo();
    // Missing: assertTrue(kryo.getReferences());
}
```

### What the bug looks like in production code:
In the `KryoSerializer.getKryoInstance()` method, the Kryo initialization may configure:
- `kryo.setRegistrationRequired(false)`
- `kryo.setInstantiatorStrategy(new StdInstantiatorStrategy())`

But forget to call `kryo.setReferences(true)`. This causes object reference tracking to be disabled, which breaks serialization of graphs with shared/cyclic references (e.g., `CircularReferenceException`, duplicate serialization of the same object instances).

### How to detect the bug:
1. Look for a `getKryoInstance()` or similar method in `KryoSerializer.java` that creates a new `Kryo` instance
2. Check if `kryo.setReferences(true)` or `kryo.getReferences()` appears in the initialization chain
3. If `setReferences` is missing, write a test that forces Kryo initialization and asserts `getReferences()` returns `true`