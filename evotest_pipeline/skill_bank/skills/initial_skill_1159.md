---
name: template-parameter-type-validation
description: When validating proxy template parameters that can be of multiple types (e.g., String and CtTypeReference), the TG should test with both type variants to ensure neither path causes issues like null pointer exceptions or processing errors.
code_tags: ['VALIDATION', 'TYPE_CONVERSION', 'STATE_MUTATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that validates or processes template/proxy parameters (e.g., from a template engine or proxy configuration) where parameters can be of different types such as `String` or `CtTypeReference` (or other polymorphic types)
- THEN the TG should write parameterized tests that pass **each type variant** as a parameter value, verifying that:
  1. The code correctly handles `String` type parameters
  2. The code correctly handles `CtTypeReference` (or other non-String object type) parameters
  3. **Both paths complete without throwing exceptions** and produce the expected result
- The test should specifically verify that when a parameter is a `CtTypeReference`, the code does not encounter a `NullPointerException` when extracting/processing its type information
- Include concrete assertions that validate the method returns the expected transformed output for both type variants

**Common pitfalls to avoid:**
- Testing only with `String` type parameters, which may hide bugs in the object-type parameter handling path
- Assuming that if one type works, all types work — the code branches may have different processing logic for different parameter types
- Missing the case where a parameter that is a type reference object is passed instead of a simple string, causing the code to attempt method calls on an object that behaves differently than a string

**Example of a correct test approach:**
```java
// Correct: Tests both String and CtTypeReference parameter types
@Test
public void testParameterValidationWithString() {
    // Test with String parameter
    String result = processor.transform("template", "param1", "myValue");
    assertEquals("expectedStringResult", result);
}

@Test
public void testParameterValidationWithTypeReference() {
    // Test with CtTypeReference parameter
    CtTypeReference typeRef = someFactory.createTypeReference("java.util.List");
    String result = processor.transform("template", "param1", typeRef);
    assertEquals("expectedTypeRefResult", result);
}
```

**Example of an incorrect approach:**
```java
// WRONG: Only tests String type, misses the CtTypeReference bug path
@Test
public void testParameterValidation() {
    // Only testing with String — won't catch the type reference bug
    String result = processor.transform("template", "param1", "myValue");
    assertEquals("expectedStringResult", result);
}
```