---
name: template-parameter-type-validation
description: When validating parameters in a protocol decoder that accepts both String and CtTypeReference types, test with various Class types to ensure type-based parameter extraction works correctly. This skill catches bugs where generic type validation fails for non-String parameter types.
code_tags: ['NULL_CHECK', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a protocol decoder method that processes parameters from a template or pattern, where parameters can be of different types (e.g., String, Class, CtTypeReference)
- THEN the TG should create a test that:
  1. Passes parameters of **multiple different types** (e.g., both `String.class` and `CtTypeReference.class` or similar type references) to the decoder method
  2. Verifies that the correct type-based extraction logic is applied for each parameter type
  3. Expects the test to **fail on the buggy version** with an exception (such as ClassCastException, NullPointerException, or incorrect decoding results) when a non-primary type is used
  4. Ensures the fix correctly handles type dispatch by comparing actual decoded output against expected values

- WHEN the TG sees code that extracts a parameter value using a type discriminator (e.g., `getParam(type, Class<T>)` or similar generic pattern)
- THEN the TG should test with at least one type that is **not the default/primary type** (e.g., if `getParam("key", String.class)` works, also test `getParam("key", Integer.class)` or `getParam("key", SomeOtherType.class)`)

- Common pitfalls to avoid:
  - Testing only with String type parameters when the method also accepts other types
  - Assuming type-based dispatch works correctly without testing at least two distinct types
  - Not asserting the exact decoded value, only checking that no exception is thrown (the bug might silently return a wrong value)
  - Not testing the specific type that caused the regression in the orginal codebase

- Correct example:
  ```java
  @Test
  public void testDecodeWithMultipleTypes() {
      // Setup decoder with a template containing parameters
      // Test with String type
      String stringResult = decoder.decode(buffer, "template", String.class);
      assertEquals("expectedString", stringResult);
      
      // Test with a non-String type (e.g., Integer, Long, or a custom type)
      Integer intResult = decoder.decode(buffer, "template", Integer.class);
      assertEquals(Integer.valueOf(123), intResult);
  }
  ```

- Incorrect example:
  ```java
  @Test
  public void testDecodeOnlyWithString() {
      // Only tests String type - misses the bug entirely
      String result = decoder.decode(buffer, "template", String.class);
      assertEquals("expectedString", result);
  }
  ```