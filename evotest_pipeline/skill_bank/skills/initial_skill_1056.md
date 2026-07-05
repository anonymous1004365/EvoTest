---
name: template-parameter-type-validation
description: When validating proxy template parameters, test with multiple data types (not just String) to ensure type-safe validation. Helps detect bugs where non-String types bypass validation logic that only checks String parameters.
code_tags: ['VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that validates or processes proxy template/placeholder parameters (e.g., map-based parameter validation, set with expected keys, or substitution logic in a template engine)
- THEN the TG should:
  1. Write a parameterized test that provides template parameters of multiple data types, including both **String** and **non-String types** (e.g., CtTypeReference, Integer, custom objects).
  2. Use the API to set parameters both as raw Strings and as typed objects (e.g., CtTypeReference objects) to verify the validation/substitution logic handles them uniformly.
  3. Verify that the correct keys/values are produced in the output regardless of parameter value type — if a parameter validation only accepts String values but the system also passes non-String objects, this is likely a bug.
  4. Expect the test to pass on the **fixed** version and fail on the **buggy** version — typically with an exception (e.g., `ClassCastException`) or with incorrect output (e.g., missing/non-functional parameters).

- Common pitfalls to avoid:
  - ❌ Testing only with `String` type parameter values — this misses bugs where non-String types (e.g., CtTypeReference) are passed and silently break validation.
  - ❌ Assuming that map-based parameter validation only needs to check key existence, not value types — the validation logic may cast values to String unconditionally.
  - ❌ Not verifying the output/result after setting parameters — the bug may manifest as missing substitutions in the final output rather than an immediate exception.
  - ❌ Using only `Mock` or `Stub` objects without exercising the actual validation/substitution logic.

### Example (Correct — catches this bug)

```java
// Template engine accepts parameters of various types
// Bug: validation cast all values to String, breaking non-String types

@Test
public void testTemplateWithMixedParameterTypes() {
    Map<String, Object> params = new HashMap<>();
    params.put("key1", "stringValue");
    params.put("key2", someCtTypeReference);  // non-String type
    
    String result = templateEngine.substitute("template {{key1}} {{key2}}", params);
    
    assertThat(result).contains("stringValue");
    assertThat(result).contains(someCtTypeReference.toString()); // or expected output
}
```

### Example (Incorrect — misses the bug)

```java
// ❌ Only tests String parameter values, does not exercise the non-String code path
@Test
public void testTemplateWithStringParamsOnly() {
    Map<String, String> params = new HashMap<>();
    params.put("key1", "value1");
    params.put("key2", "value2");
    
    String result = templateEngine.substitute("template {{key1}} {{key2}}", params);
    
    assertThat(result).contains("value1");
    assertThat(result).contains("value2");
    // This test passes even on the buggy version, giving false confidence
}
```