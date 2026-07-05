---
name: template-parameter-type-validation
description: When validating proxy template parameters for a factory method, test with both actual and potential parameter types to ensure all branches of type-specific logic are covered. This skill helps catch bugs where template parameter validation only handles some expected types, missing edge cases like intermediate or newly introduced types.
code_tags: ['NULL_CHECK', 'VALIDATION', 'EXCEPTION_HANDLING']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a factory method that accepts a `Map<String, Object>` of parameters (or similar generic collection of key-value pairs), where certain keys have expected types (e.g., `CtTypeReference`, `String`, `Integer`), and the method validates or processes these parameters with type-specific logic (e.g., `instanceof` checks, type casting, or type-based dispatching):
  - THEN the TG should write a test that calls the factory method with parameters of BOTH the expected type AND other types that might appear in practice (e.g., if the code expects some parameters of type `CtTypeReference`, test by passing parameters of that type; but ALSO test parameters of type `String`, and vice versa).
  - The test should verify that the factory method correctly validates and handles all supplied parameter types without throwing unexpected exceptions (e.g., `ClassCastException`, `NullPointerException`, `ArrayStoreException`, `IllegalArgumentException`).
  - Include at least one test case where the parameter types intentionally mismatch the method's expected types to exercise type-checking branches.
  - Verify the factory method produces a valid output object (not null) when types are correct, and throws an appropriate exception or returns a sensible fallback when types are incorrect.

- Common pitfalls to avoid:
  - Testing ONLY the "happy path" with perfectly typed parameters (e.g., only `CtTypeReference` parameters), while ignoring that parameters may arrive as `String` objects in practice.
  - Assuming that a `Map<String, Object>` will always contain values of a single type — testers should mix types.
  - Forgetting to verify the final state of the created object (e.g., checking that a specific field was set correctly) in addition to the absence of exceptions.
  - Using `assertNull` or expecting an exception when the code might silently produce a wrong object — always verify the object's correctness, not just the absence of crashes.

- Example of a correct test (pseudocode):
  ```java
  @Test
  public void testParameterTypeValidation() {
      // Test with expected type
      CtTypeReference<Class<?>> typeRef = ...;
      Map<String, Object> params = new HashMap<>();
      params.put("templateType", typeRef);
      MyFactory factory = new MyFactory();
      MyObject obj = factory.create(params);
      assertNotNull(obj);
      assertEquals(typeRef, obj.getTemplateType());

      // Test with alternative type (e.g., String)
      Map<String, Object> params2 = new HashMap<>();
      params2.put("templateType", "SomeClassName");
      // Should handle gracefully, not crash with ClassCastException
      MyObject obj2 = factory.create(params2);
      assertNotNull(obj2);
  }
  ```

- Example of an incorrect test (too narrow):
  ```java
  @Test
  public void testTemplateParameters_OnlyCtTypeReference() {
      Map<String, Object> params = new HashMap<>();
      params.put("templateType", someCtTypeRef);
      MyObject obj = factory.create(params);
      assertNotNull(obj);
      // ❌ Missing test with String parameter — bug may go undetected
  }
  ```