---
name: null-check-for-property-deserializers
description: When a serializer/deserializer uses a property name or type to look up
  another serializer, the found value may be null. Tests should verify that null values
  are handled gracefully (with NullPointerException logging or fallback) rather than
  causing failures.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: EXCEPTION_TEST
---

# null-check-for-property-deserializers

## Instructions

# Null Check for Property Deserializers

## Instructions

- WHEN the TG encounters a deserializer/serializer class that looks up a sub-serializer by property name, type, or key (e.g., using a map lookup or factory method based on a dynamic value), THEN the TG should test with values that cause the lookup to return null, verifying the code does NOT throw a NullPointerException or other unhandled exception.

- WHEN testing a serializer that calls methods like `getDeserializer(key)`, `getSerializer(key)`, `createSerializer(type)`, or similar factory lookup patterns, THEN the TG should pass unknown/unregistered property names, null keys, or edge-case type values and assert that the code handles the null return gracefully (e.g., returns a default, skips the field, or logs without crashing).

- Common pitfalls to avoid:
  - Testing only with well-known/expected property values that return valid sub-serializers, missing the null-return path entirely.
  - Assuming a map lookup will always succeed because the test uses a "correct" value.
  - Not testing the actual method that the buggy code fails on — verify the exact method chain that can produce a null reference.

- Example of a correct test:
  ```java
  @Test
  public void testWithUnknownProperty() {
      // Given a serializer/deserializer that looks up sub-serializers by key
      SerializerFactory factory = new SerializerFactory();
      // When passing an unknown/unregistered key
      // Then it should NOT throw NullPointerException
      assertDoesNotThrow(() -> factory.createSerializer("unknownType"));
  }
  ```

- Example of an incorrect test (missing the null check):
  ```java
  @Test
  public void testWithKnownProperty() {
      // This only tests the happy path — misses the null-return bug
      SerializerFactory factory = new SerializerFactory();
      Object serializer = factory.createSerializer("knownType");
      assertNotNull(serializer);
  }
  ```