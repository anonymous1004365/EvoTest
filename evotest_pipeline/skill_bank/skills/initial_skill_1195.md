---
name: constructor-parameter-type-validation
description: When a test exercises Jackson deserialization with constructors that
  bind to mismatched types (e.g., int vs String), the test should verify JsonMappingException
  is thrown for the mismatched field. Use this skill when testing deserialization
  of POJOs with multiple constructor parameters having different types.
code_tags:
- NULL_CHECK
- STATE_MUTATION
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# constructor-parameter-type-validation

## Instructions

# Constructor Parameter Type Validation in Jackson Deserialization

## Instructions

- WHEN the TG encounters a test that deserializes JSON into a POJO using a constructor (e.g., `@JsonCreator` constructor with `@JsonProperty` parameters), and one or more constructor parameters have incompatible types (e.g., a JSON string field mapped to an `int` constructor parameter, or vice versa)
- THEN the TG should write a test that:
  - Creates a JSON string with a **mismatched type** value for at least one constructor parameter (e.g., `"intField": "notanumber"` instead of `"intField": 1`).
  - Calls the deserialization method (e.g., `new ObjectMapper().readValue(json, SimplePojo.class)`).
  - Asserts that a `JsonMappingException` (or `com.fasterxml.jackson.databind.JsonMappingException`) is thrown, caused by a lower-level type conversion exception (e.g., `NumberFormatException`).
  - Also verifies the exception message contains the mismatched field name and the target type (e.g., `"intField"`, `"Integer"`, or `"int"`).
- WHEN the TG tests a POJO with an `@JsonCreator` constructor that has multiple typed parameters
- THEN the TG should include at least one test case where a numeric field gets a non-numeric string value, and at least one test case where a string field gets a numeric value, to cover both directions of type mismatch.
- Common pitfalls to avoid:
  - Testing only valid deserialization scenarios without any type mismatch validation tests.
  - Forgetting that `JsonMappingException` wraps the actual cause — assert on the wrapper exception type, not the inner exception type.
  - Testing type mismatch only for one parameter when multiple parameters with different types exist (e.g., only testing `stringField` but not `intField`).
  - Using generic `Exception` in `assertThrows` instead of the specific `JsonMappingException`.
- Example correct test snippet (pseudocode):

```java
// For a POJO: SimplePojo(int intField, String stringField)
@Test
public void testInvalidIntField() {
    String json = "{ \"intField\": \"notanumber\", \"stringField\": \"foo\" }";
    assertThrows(JsonMappingException.class, () -> {
        new ObjectMapper().readValue(json, SimplePojo.class);
    });
}
```

- Example incorrect test snippet:

```java
// WRONG: Tests only the valid case, misses the bug
@Test
public void testDecode() {
    String json = "{ \"intField\": 1, \"stringField\": \"foo\" }";
    SimplePojo result = new ObjectMapper().readValue(json, SimplePojo.class);
    assertEquals(1, result.getIntField());
    assertEquals("foo", result.getStringField());
    // No type mismatch test — buggy code that fails on bad types goes undetected
}
```