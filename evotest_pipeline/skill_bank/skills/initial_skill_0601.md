---
name: template-proxy-parameter-type-validation
description: When a method accepts parameters of type `Object` but internally casts or processes them as a specific type (e.g., `CtTypeReference`), the TG should test with both valid and invalid types to ensure proper validation. This skill prevents bugs where invalid types silently pass validation.
code_tags: ['VALIDATION']
test_pattern: EXCEPTION_TEST
---

# template-proxy-parameter-type-validation

## Instructions

# Template Proxy Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that accepts a parameter typed as `Object` but internally casts or processes it as a specific type, such as `CtTypeReference`, `String`, or a collection of a specific element type
- THEN the TG should write parameterized tests passing values of the **wrong type** and verify that an appropriate exception (e.g., `ClassCastException`, `IllegalArgumentException`) is thrown, or that the method correctly handles them without producing incorrect output
- Include tests for:
  1. Passing values of the correct type (happy path)
  2. Passing values of an incorrect but related type (e.g., passing a `String` where `CtTypeReference` is expected)
  3. Passing `null` values where relevant
- Common pitfalls:
  - Testing only with valid types and missing the case where invalid types silently pass through and cause downstream failures
  - Assuming that because a parameter is `Object`, any type is acceptable — when the implementation actually expects a specific type
- Example correct test:
  ```java
  @Test(expected = ClassCastException.class)
  public void testInvalidParameterType() {
      Proxy proxy = ...;
      // Passing String instead of CtTypeReference should fail
      proxy.setActualTypeArguments("invalid");
  }
  ```
- Example incorrect test:
  ```java
  @Test
  public void testValidParameterType() {
      Proxy proxy = ...;
      CtTypeReference<String> ref = factory.Type().createReference(String.class);
      proxy.setActualTypeArguments(ref);
      // This is good but insufficient — missing invalid type test
  }
  ```