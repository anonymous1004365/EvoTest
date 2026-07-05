---
name: template-parameter-type-validation
description: When validating or processing template parameters that can hold different types (e.g. Strings, objects), test with all supported types to avoid ClassCastException from unchecked casts. Use when iterating over parameter values or looking up values by type.
code_tags: ['ARGUMENT_VALIDATION', 'STATE_MUTATION', 'BOUNDARY_CHECK', 'VALIDATION', 'TYPE_CONVERSION', 'NULL_CHECK']
test_pattern: EXCEPTION_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that iterates over a collection of template/protocol parameters and looks up a value using both a generic type (e.g. String) AND a specific type (e.g. CtTypeReference, device ID, enum), or when a template parameter map can contain values of different types
- THEN the TG MUST write a test that provides the expected parameter value as BOTH:
  1. A simple String/primitive type (e.g. `"myValue"`)
  2. A different specific type (e.g. `someCtTypeReference`, `someChannelBuffer`)
  - The test should verify that calling the decode/template-filling method with mixed-type parameters does NOT throw a `ClassCastException` on the fixed version
  - The test should specifically use a type that the code tries to cast or match against (e.g. if the code does `String value = (String) map.get(key)`, test with a non-String value in the map)

- Common pitfalls to avoid:
  - Testing only String type parameters when the protocol accepts multiple parameter types
  - Not providing both a simple type AND a complex type parameter in the same test
  - Assuming the code correctly handles type-safe access without verifying it with actual different types
  - Not testing with the specific type that appears in a `get`/`lookup` call that fails due to an unchecked cast

### Example (correct test pattern):

```java
// Correct: Tests with both String and Object types in the same decode call
public void testDecodeWithMixedParameterTypes() throws Exception {
    // Create parameters with both String and CtTypeReference types
    Map<String, Object> params = new HashMap<>();
    params.put("param1", "testValue");                          // String type
    params.put("param2", factory.createCtTypeReference(...));  // Object/CtTypeReference type
    params.put("param3", ChannelBuffers.copiedBuffer(...));    // ChannelBuffer type
    
    // The decode method may iterate params.values() and try to cast them.
    // On the buggy version this would throw ClassCastException.
    Object result = decoder.decode(params, ...);
    assertNotNull(result);
}
```

### Example (incorrect pattern — doesn't catch the bug):

```java
// WRONG: Only tests with String parameters, won't trigger the bug
public void testDecode() throws Exception {
    Map<String, Object> params = new HashMap<>();
    params.put("param1", "testValue");
    params.put("param2", "anotherValue");  // Only String types
    
    Object result = decoder.decode(params, ...);
    assertNotNull(result);
    // Test passes even on buggy version because no ClassCastException occurs
}
```