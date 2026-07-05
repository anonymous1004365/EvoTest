---
name: proxy-template-parameter-validation
description: WHEN the TG encounters a proxy/template pattern where generic parameters
  of different specific types are passed to a method, THEN it should test each distinct
  parameter type to ensure the method handles them correctly, verifying that validation
  logic is applied uniformly across all supported types.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# proxy-template-parameter-validation

## Instructions

# Proxy Template Parameter Validation

## Instructions

- WHEN the TG encounters a method that accepts parameters of a generic type (e.g., `Object`, `T`, wildcard types) and the method is part of a proxy, template, or decoder pattern:
  - THEN the TG should write parameterized tests that exercise the method with each distinct concrete type that the method is expected to handle in production.
  - Include edge cases such as `null` values, empty strings, values at boundary limits, and values with special characters.
  - Verify that the method does not throw unexpected exceptions (like `NullPointerException`, `ArrayIndexOutOfBoundsException`, or `ClassCastException`) when given valid inputs of different types.
  - Verify that validation logic (e.g., checks for allowed values, range checks, format checks) is correctly applied to ALL parameter types, not just the most common one.

- Common pitfalls:
  - Testing only with `String` type parameters when the method also accepts numeric types, enums, or custom objects.
  - Testing only valid inputs and not testing boundary or invalid inputs.
  - Assuming that if the method works for one type, it works for all types without explicit verification.
  - Forgetting to test `null` inputs when the method should handle them gracefully.

- Example correct test pattern:

```java
@ParameterizedTest
@CsvSource({
    "type1, value1, expected1",
    "type2, value2, expected2",
    "type3, value3, expected3"
})
void testMethodWithMultipleTypes(String type, String value, String expected) {
    // Setup
    MyDecoder decoder = new MyDecoder();
    
    // Execute
    Object result = decoder.decode(type, value);
    
    // Verify
    assertEquals(expected, result.toString());
}
```

- Example incorrect test pattern (insufficient):

```java
// INCORRECT: Only tests with String type, assumes other types work
@Test
void testMethodWithStringOnly() {
    MyDecoder decoder = new MyDecoder();
    Object result = decoder.decode("string", "hello");
    assertEquals("hello", result.toString());
    // Does not verify behavior with numeric or other types
}
```