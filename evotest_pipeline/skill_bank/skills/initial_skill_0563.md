---
name: serialization-state-field-mutation
description: When a class is serialized/deserialized and a field's value changes between
  serialization and deserialization (due to construction or default values), tests
  should verify that the deserialized object matches the original. Apply when JSON
  or similar serialization omits fields that are reconstructed with different values.
code_tags:
- STATE_MUTATION
- TYPE_CONVERSION
- VALIDATION
- JSON_SERIALIZATION_VERSIONING
test_pattern: STATE_TEST
---

# serialization-state-field-mutation

## Instructions

# Serialized State Mutation After Deserialization

## Instructions

- WHEN a class contains fields that are computed or set during construction (not stored in serialized form), AND the class is serialized/deserialized via a format like JSON or Gson
- THEN write a test that:
  1. Creates an instance of the class normally (via constructor)
  2. Serializes the instance to a string (e.g., JSON)
  3. Deserializes the string back to a new instance
  4. Compares relevant fields of the original and deserialized instance using assertions
  5. Pay special attention to fields that might be set to default values during deserialization (e.g., `-1`, `0`, `null`) vs. the values they held after normal construction

- **Concrete example** (based on SourcePosition classes):
  - The class has a `sourceEnd` field that defaults to `-1` and is only set after construction via a separate setter.
  - When serialized as JSON and deserialized back via Gson, the `sourceEnd` field may be `-1` (default) because the serialized JSON doesn't include it or the deserializer doesn't restore it properly.
  - The test should create an object, set `sourceEnd` to a non-default value (e.g., `42`), serialize it, deserialize it, then assert that `deserialized.getSourceEnd() == 42`.

- **Common pitfalls**:
  - Assuming that serialization round-trips are identity-preserving for all fields — some fields may be excluded from serialization or deserialized to default values.
  - Testing only with fields that have default/zero values, missing the bug where non-default values are lost.
  - Not testing the round-trip (serialize → string → deserialize) and only testing serialization OR deserialization in isolation.
  - Using `assertEquals` on the entire object without checking specific fields that are known to be problematic.

- **Incorrect test** (does NOT catch the bug):
  ```java
  SourcePosition pos = new SourcePosition(new Source(null, new File("test")));
  String json = gson.toJson(pos);
  SourcePosition deserialized = gson.fromJson(json, SourcePosition.class);
  // Only checks that deserialization doesn't crash — doesn't verify field values
  assertNotNull(deserialized);
  ```

- **Correct test** (catches the bug):
  ```java
  SourcePosition pos = new SourcePosition(new Source(null, new File("test")));
  pos.setSourceEnd(42);  // set non-default value
  String json = gson.toJson(pos);
  SourcePosition deserialized = gson.fromJson(json, SourcePosition.class);
  // Bug: sourceEnd may be -1 after deserialization because the field is not properly serialized
  assertEquals("sourceEnd should be preserved through serialization", 
                42, deserialized.getSourceEnd());
  ```