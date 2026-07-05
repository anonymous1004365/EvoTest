---
name: binary-type-coercion-validation
description: When binary property values are retrieved via Property.getBinary() but
  internally stored as String, the implicit type coercion can fail or produce broken
  Binary objects. Use this skill to test that mixed-type property coercion works correctly
  for both String and Binary types.
code_tags:
- ARGUMENT_VALIDATION
- BOUNDARY_CHECK
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# binary-type-coercion-validation

## Instructions

# Binary Type Coercion Validation

## Instructions

- WHEN the TG encounters a `Property.getBinary()` call that may return a Binary object derived from a non-Binary internal value (e.g., a String stored in the same property), or when `Property.getValue()` can return values of different types depending on how the property was set
- THEN the TG should write a test that:
  1. Sets a JCR property using `session.getRootNode().setProperty("propName", "someString")` (String value)
  2. Retrieves the same property via `Property.getBinary()` (or `Property.getValue()`)
  3. Calls `Binary.getStream()` and reads the stream content
  4. Asserts that the returned content matches the original string
  5. Verifies that `Binary.getStream()` returns a non-null InputStream
- Include concrete values: use `"testString"` or similar as the property value, and `session.getRootNode().setProperty("testProp", value)` as the setter
- Common pitfalls to avoid:
  - Testing only with `ValueFactory.createValue()` (Binary-typed values) instead of also testing with plain String property values
  - Forgetting that `Property.getBinary()` can be called on String-typed properties (JCR allows coercion)
  - Not checking that the Binary stream is readable/non-null after coercion
  - Testing only one direction (String→Binary) when the property may be set as Binary and read as String in other tests — focus on the coercion direction that matches the bug

## Example (Correct — catches the bug)

```java
// Test that String property values can be coerced to Binary
@Test
public void testStringToBinaryCoercion() throws RepositoryException {
    Session session = getAdminSession();
    Node node = session.getRootNode();
    
    // Set as String
    node.setProperty("stringProp", "Hello World");
    session.save();
    
    // Read back as Binary (coercion)
    Property prop = node.getProperty("stringProp");
    Binary binary = prop.getBinary();
    assertNotNull("Binary should not be null", binary);
    
    InputStream stream = binary.getStream();
    assertNotNull("Stream should not be null", stream);
    
    String result = new String(stream.readAllBytes(), StandardCharsets.UTF_8);
    assertEquals("Hello World", result);
    
    binary.dispose();
}
```

## Example (Incorrect — misses the bug)

```java
// BUGGY: Only tests Binary-to-Binary roundtrip, missing String→Binary coercion
@Test
public void testBinaryProperty() throws RepositoryException {
    Session session = getAdminSession();
    Binary binary = session.getValueFactory().createBinary(
        new ByteArrayInputStream("test".getBytes()));
    session.getRootNode().setProperty("binProp", binary);
    session.save();
    
    Binary result = session.getRootNode().getProperty("binProp").getBinary();
    assertNotNull(result);
    result.dispose();
}
```