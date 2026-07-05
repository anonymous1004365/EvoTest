---
name: template-parameter-type-validation
description: When validating or processing proxy template parameters (e.g. Map<String, Object>), test that the parameter type is a CtTypeReference and not just a String. Without this check, the code can cast a String parameter to CtTypeReference and trigger a ClassCastException.
code_tags: ['NULL_CHECK', 'VALIDATION', 'STATE_MUTATION']
test_pattern: EXCEPTION_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that processes `Map<String, Object>` parameters from a template, proxy, or configuration context (where values can be either `String` or `CtTypeReference` types) and iterates over the entry set casting values directly to `CtTypeReference`:
  - THEN the TG should write a test that passes **both** a `String`-typed value and a `CtTypeReference`-typed value as parameter values, and verify that the method handles the `String` type without throwing a `ClassCastException`.
  - The test should verify that when a `String` value is provided (e.g., `"java.lang.String"`), the code does not blindly cast it to `CtTypeReference` but instead checks the type first using `instanceof` or equivalent.
  - The failure on the buggy version will be a `ClassCastException: class java.lang.String cannot be cast to class spoon.reflect.reference.CtTypeReference`.
  - **Common pitfalls to avoid:**
    - Testing only with `CtTypeReference` parameter values and missing the `String` case (which is the buggy path).
    - Assuming the method uses type-safe generics (e.g., `Map<String, CtTypeReference>`) when the actual signature is `Map<String, Object>`.
    - Writing a test that only passes without asserting the correct behavior (e.g., silent success when it should fail gracefully).

- **Correct example (should pass on fixed code, fail on buggy):**
  ```java
  @Test
  public void testStringParameterCausesClassCastException() {
      TotemProtocolDecoder decoder = new TotemProtocolDecoder(null);
  
      Map<String, Object> params = new HashMap<>();
      params.put("type", "java.lang.String");  // String instead of CtTypeReference
      params.put("otherKey", factory.Type().stringType());  // CtTypeReference
  
      assertThrows(ClassCastException.class, () -> {
          decoder.someMethod(params);
      });
  }
  ```

- **Incorrect example (would pass on buggy code too — missing the String type):**
  ```java
  @Test
  public void testOnlyCtTypeReferenceParameters() {
      TotemProtocolDecoder decoder = new TotemProtocolDecoder(null);
  
      Map<String, Object> params = new HashMap<>();
      params.put("type", factory.Type().stringType());  // Only CtTypeReference values
  
      decoder.someMethod(params);
      // No assertion needed — this always passes
  }
  ```

- **When fixing the production code**: the method should check `value instanceof CtTypeReference` before casting. If the value is a `String`, it should handle it appropriately (e.g., convert to `CtTypeReference` using the factory, or throw a meaningful exception).