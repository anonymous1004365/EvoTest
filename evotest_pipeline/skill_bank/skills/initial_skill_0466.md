---
name: template-parameter-type-validation
description: When a method accepts parameters that can be either a map-like object (containing a UUID key) or a direct object reference, test both input formats to ensure proper deserialization/handling. Use this skill to catch bugs where an overloaded method or code path fails to handle one of the valid input formats.
code_tags: ['VALIDATION', 'STATE_MUTATION', 'TYPE_CONVERSION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that accepts a parameter that can be provided in multiple formats (e.g., as a simple identifier string/object OR as a map-like structure containing an identifier key like `"uuid"`):
  - THEN the TG should write a test that passes the parameter in the map-like format (e.g., a JSON object or Map with the key `"uuid"`) and verifies the operation succeeds.
  - The test should specifically call the resource's method with a parameter that is a `Map<String, String>` containing at least the key `"uuid"` mapped to a valid UUID string.
  - Verify that the method correctly extracts the UUID and proceeds without throwing an exception (e.g., `IllegalArgumentException`, `NullPointerException`, `ClassCastException`).
  - A common pitfall is testing only with direct string/object parameters and missing the map-based input format. Always test both formats when the API supports both.

### Correct Example

```java
// When testing a resource method that accepts either a direct object or a map with a "uuid" key:
@Test
public void testWithMapParameter() {
    Map<String, String> params = new HashMap<>();
    params.put("uuid", "some-valid-uuid-value");
    // Call the method under test
    Object result = resource.getByUniqueId(params);
    assertNotNull("Should handle map-based parameter", result);
}
```

### Incorrect Example

```java
// WRONG: Only testing with direct string parameter
@Test
public void testWithDirectParameter() {
    Object result = resource.getByUniqueId("some-valid-uuid-value");
    assertNotNull(result);
    // Missing test with map parameter — buggy path not exercised
}
```