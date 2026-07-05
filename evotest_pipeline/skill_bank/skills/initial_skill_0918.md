---
name: plugin-object-serialization-check
description: When a plugin creates objects that are serialized (e.g., via SerializedLayout
  or ObjectOutputStream), the TG should verify that all plugin-created objects implement
  java.io.Serializable. The skill is used when testing components that serialize LogEvent
  objects created via the plugin framework.
code_tags:
- ARGUMENT_VALIDATION
- ARRAY_INDEX_ACCESS
- BOUNDARY_CHECK
test_pattern: EXCEPTION_TEST
---

# plugin-object-serialization-check

## Instructions

# Plugin Object Serialization Check

## Instructions

- WHEN the TG encounters a test that serializes `LogEvent` objects (e.g., using `SerializedLayout.toByteArray(LogEvent)`, `ObjectOutputStream.writeObject(LogEvent)`, or `SerializedLayout.createLayout()`), AND the LogEvent is built from a plugin-created object (e.g., via `AbstractConfiguration.createPluginObject()` / `PluginBuilder`)  
  THEN the TG should write a test that:
  1. Creates a `LogEvent` using `Log4jLogEvent.newBuilder()` with a `Message` that contains a plugin-created parameter (e.g., an object created via the plugin system like `CtTypeReference` a custom `ObjectMessage`, or any object that might not implement `java.io.Serializable`)
  2. Passes this event to `SerializedLayout.toByteArray(event)` or equivalent serialization
  3. Verifies that serialization completes without throwing `java.io.NotSerializableException`

- WHEN writing such a test, include concrete types: use `SerializedLayout.createLayout()` (from `org.apache.logging.log4j.core.layout.SerializedLayout`), `Log4jLogEvent.newBuilder()` (from `org.apache.logging.log4j.core.impl.Log4jLogEvent`), and `SimpleMessage` or `ObjectMessage` (from `org.apache.logging.log4j.message`)

- WHEN the test involves plugin objects that are passed as parameters (e.g., via `PluginBuilder` which is in `org.apache.logging.log4j.core.config.plugins.util.PluginBuilder`), verify that ALL types used in the message or event implement `java.io.Serializable`. If any type in the chain is not serializable, the test should fail with a `java.io.NotSerializableException` on the buggy version.

- Common pitfalls to avoid:
  - Testing only with `SimpleMessage` containing a plain `String` — this passes trivially and misses plugin-created non-serializable types
  - Not using `ObjectOutputStream` directly in the test to verify `Serializable` contract when `SerializedLayout` swallows `IOException` (note: `SerializedLayout.toByteArray()` catches `IOException` and logs it, returning an empty array silently — so the test MUST check the returned byte array is non-empty and deserializable, not just that no exception was thrown from the call itself)
  - Forgetting that `SerializedLayout.toByteArray()` catches `IOException` internally — the test should assert `result.length > 0` and then deserialize the result to verify it worked, otherwise a failure to serialize could be silently swallowed

### Correct Example (catches the bug):
```java
@Test
public void testPluginObjectSerialization() throws Exception {
    // Create a LogEvent with a message that contains plugin-created objects
    // (e.g., CtTypeReference, custom non-serializable types)
    final LogEvent event = Log4jLogEvent.newBuilder()
        .setLoggerName("test")
        .setLoggerFqcn("org.apache.logging.log4j.core.Logger")
        .setLevel(Level.INFO)
        .setMessage(new ObjectMessage(new SomePluginObject()))
        .build();
    
    final SerializedLayout layout = SerializedLayout.createLayout();
    final byte[] result = layout.toByteArray(event);
    
    // IMPORTANT: toByteArray swallows IOException, so check result
    assertTrue("Serialization failed - result is empty", result.length > 0);
    
    // Verify the result can be deserialized
    final ByteArrayInputStream bais = new ByteArrayInputStream(result);
    final ObjectInputStream ois = new ObjectInputStream(bais);
    final LogEvent deserialized = (LogEvent) ois.readObject();
    assertNotNull(deserialized);
}
```

### Incorrect Example (misses the bug):
```java
@Test
public void testSerialization() throws Exception {
    // Only tests with a plain string message - works even when plugins fail
    final LogEvent event = Log4jLogEvent.newBuilder()
        .setLoggerName("test")
        .setLevel(Level.INFO)
        .setMessage(new SimpleMessage("Hello"))
        .build();
    
    final SerializedLayout layout = SerializedLayout.createLayout();
    final byte[] result = layout.toByteArray(event);
    assertNotNull(result);  // Does NOT check result.length > 0!
    
    // When serialization fails, toByteArray returns an empty byte[],
    // not null, so this assertion passes even on the buggy version.
    
    // Missing: deserialization verification
}
```