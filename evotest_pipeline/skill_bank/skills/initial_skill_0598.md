---
name: jdk-unsupported-serialization-type
description: When a custom Java 8+ date/time type (like java.time.Instant) is serialized
  without proper Jackson module registration, the serializer must be explicitly configured.
  This skill teaches how to verify that Jackson correctly serializes/deserializes
  user-defined types when using primitive-like creator properties.
code_tags:
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# jdk-unsupported-serialization-type

## Instructions

# Jackson Creator Property Resolution for Primitive-Like Types

## Instructions

- WHEN the TG encounters code that uses Jackson's `@JsonCreator` with `@JsonProperty` on constructor parameters that have `java.time.Instant` or other Java 8+ date/time types (or similar wrapper/value types)
- THEN the TG should write a test that passes such a type as a creator property and verifies that:
  1. A `JsonMappingException` is thrown on the buggy version due to type resolution failure, OR
  2. The deserialization succeeds on the fixed version with the proper module registration
- Specifically, for `java.time.Instant` fields with `@JsonCreator`, deserialization may fail with `JsonMappingException` because Jackson cannot find a creator property with that name — due to a mismatch between the property name resolution for `java.time.Instant` and primitive types.
- The test should use a POJO with an `Instant` field (or similar) annotated with `@JsonProperty` in a `@JsonCreator` constructor, and attempt to deserialize a JSON string containing that field.
- **Common pitfalls to avoid**:
  - Testing only with `String` or primitive types in creator constructors — the bug manifests specifically with `java.time.Instant` and similar value types
  - Forgetting to check for `JsonMappingException` which wraps the specific "Could not find creator property with name" error
  - Assuming that `@JsonProperty` alone is sufficient for all types without testing the actual deserialization path
- **Example** (correct): A test that deserializes `{"intField": 1, "stringField": "foo"}` into a POJO with `@JsonCreator` constructor `(@JsonProperty("intField") Instant intField, @JsonProperty("stringField") String stringField)` — which should fail on buggy version with `JsonMappingException` because the `Instant` type is not resolved correctly as a creator property.
- **Example** (incorrect): Testing only with `String` and `int` fields in the creator constructor, missing the bug entirely.