---
name: template-parameter-type-validation
description: When validating template parameters (e.g., proxy template parameters parsed from URIs), test that both primitive String values and complex types (e.g., CtTypeReference) are handled correctly — not just String types. The test should verify that the parameter value is properly converted/processed regardless of its type.
code_tags: ['ARGUMENT_VALIDATION', 'BOUNDARY_CHECK', 'NULL_CHECK']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that processes or validates template parameters (e.g., URI template variables, proxy template parameters, or similar named parameter maps) — especially when the parameters come from a `Map<String, Object>` where values can be of different types
- THEN the TG should write a parametric test that passes parameters with different concrete types through the validation/processing method. Include at least:
  - A `String` value (the expected/common case)
  - A non-String object value (e.g., CtTypeReference, Integer, or custom type)
- Verify that each parameter type is processed correctly without throwing unexpected exceptions (e.g., ClassCastException, NullPointerException, or silent failure)
- On the buggy version, the test with non-String types should fail — typically the validation only handles String values and crashes or returns wrong results for other types
- Common pitfalls:
  - Testing only with String parameters, which works but misses the bug entirely
  - Assuming all template parameter values are Strings
  - Not iterating through all entries in a parameter map

### Example (Correct)
```java
// Test with multiple parameter types:
Map<String, Object> params = new HashMap<>();
params.put("name", "testValue");  // String
params.put("type", someCtTypeReference);  // Complex type

// Call the validation/processing method
// Verify no exception is thrown and parameters are correctly stored
result = processor.process(params);
assertThat(result).isNotNull();
assertThat(result.getParameter("name")).isEqualTo("testValue");
assertThat(result.getParameter("type")).isEqualTo(someCtTypeReference);
```

### Example (Incorrect — misses the bug)
```java
// Only testing with String values — this will pass on buggy code too!
Map<String, Object> params = new HashMap<>();
params.put("name", "testValue");  
params.put("type", "StringClassName");

// Buggy code only handles String values, but this test never finds out
result = processor.process(params);  // Passes on both buggy and fixed versions
```