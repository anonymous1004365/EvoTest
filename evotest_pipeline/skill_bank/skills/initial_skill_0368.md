---
name: custom-serialization-consistency
description: When a class implements custom writeObject/readObject methods that serialize
  transient fields, the serialization must be tested for consistency. This skill teaches
  how to test that a serialized-then-deserialized object equals the original and preserves
  all key fields.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: STATE_TEST
---

# custom-serialization-consistency

## Instructions

# Custom Serialization Consistency

## Instructions

- WHEN the TG encounters a class that implements `private void writeObject(ObjectOutputStream)` AND `private void readObject(ObjectInputStream)` methods to handle custom serialization of transient fields (e.g., `transient Object[] argArray` serialized as `String[] stringArgs`)
- THEN the TG should write a serialization round-trip test that:
  1. Creates an instance of the class with specific constructor arguments (e.g., `new StringFormattedMessage("Msg", "a", "b", "c")`)
  2. Serializes it to a `ByteArrayOutputStream` using `ObjectOutputStream`
  3. Deserializes it back from a `ByteArrayInputStream` using `ObjectInputStream`
  4. Asserts that the deserialized object equals the original (`assertEquals(expected, actual)`)
  5. Asserts that `getFormat()` returns the same value on both objects
  6. Asserts that `getFormattedMessage()` returns the same value on both objects
  7. Asserts that `getParameters()` returns the same values on both objects (`assertArrayEquals(expected.getParameters(), actual.getParameters())`)

- Common pitfalls to avoid:
  - **Only testing equality** without also checking `getFormat()`, `getFormattedMessage()`, and `getParameters()` individually. The `equals()` method may rely on `stringArgs` (the serialized field), but `getFormattedMessage()` may fail if the `formattedMessage` transient field is not properly reconstructed during deserialization.
  - **Testing with no-arg instances** — the bug may only manifest when the object carries specific data (e.g., non-null parameter arrays).
  - **Forgetting the transient nature** — fields marked `transient` (like `argArray`, `formattedMessage`, `throwable`) are NOT serialized by `defaultWriteObject()`. The custom `writeObject`/`readObject` methods must explicitly handle them. The test should verify that these transient-derived values are correctly reconstructed after deserialization.

- Correct example (Java):
```java
@Test
public void testSerialization() throws IOException, ClassNotFoundException {
    final StringFormattedMessage expected = new StringFormattedMessage("Msg", "a", "b", "c");
    final ByteArrayOutputStream baos = new ByteArrayOutputStream();
    try (final ObjectOutputStream out = new ObjectOutputStream(baos)) {
        out.writeObject(expected);
    }
    final ByteArrayInputStream bais = new ByteArrayInputStream(baos.toByteArray());
    final ObjectInputStream in = new ObjectInputStream(bais);
    final StringFormattedMessage actual = (StringFormattedMessage) in.readObject();
    Assert.assertEquals(expected, actual);
    Assert.assertEquals(expected.getFormat(), actual.getFormat());
    Assert.assertEquals(expected.getFormattedMessage(), actual.getFormattedMessage());
    Assert.assertArrayEquals(expected.getParameters(), actual.getParameters());
}
```

- Incorrect example that misses the bug:
```java
// BAD: Only checks equality, which relies on stringArgs (already serialized)
// Does NOT check getFormattedMessage() which might fail if formattedMessage transient is broken
@Test
public void testSerialization() throws ... {
    // ... serialize/deserialize ...
    Assert.assertEquals(expected, actual);  // This might pass even if formatted message is broken
    // Missing: assertArrayEquals on parameters, assertEquals on getFormattedMessage
}
```