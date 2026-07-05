---
name: template-parameter-type-validation
description: Use this skill when a method accepts parameters of different types (like String and CtTypeReference) and must check type identity or validity for each type. The TG should test with all relevant parameter types to ensure proper validation logic.
code_tags: ['VALIDATION', 'BOOLEAN_LOGIC', 'ORDER_DEPENDENCY']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that accepts parameters of multiple expected types (e.g., both `String` and `CtTypeReference<?>` in a `validate` or `check` method) and the implementation uses type identity checks like `if (param instanceof CtTypeReference)`
- THEN the TG should write a parametrized test that tests the method with each distinct parameter type. If the method exhibits different behavior depending on the type (e.g., throwing an exception for invalid `String` inputs but not for `CtTypeReference`), the test must verify both code paths explicitly.
- Include concrete test cases that supply:
  - A valid `String` value (that should pass validation)
  - An invalid/null `String` value (that should trigger failure/exception)
  - A valid `CtTypeReference<?>` value (that should pass validation)
  - An invalid/null `CtTypeReference<?>` value (that should trigger failure/exception)
- Verify that the method throws the correct exception type (e.g., `NullPointerException`, `IllegalArgumentException`) or returns the expected result for each type.
- Common pitfalls: 
  - Testing only one type of parameter (e.g., only `String`) and missing validation bugs in the other type branch.
  - Using the same assertion logic for both types without considering that they might take different code paths.
  - Not testing edge cases like `null` values for each parameter type separately.

### Correct example (Java with JUnit 5):
```java
@ParameterizedTest
@MethodSource("provideParameters")
void testValidateWithDifferentTypes(Object parameter, Class<? extends Throwable> expectedException) {
    if (expectedException == null) {
        assertDoesNotThrow(() -> validator.validate("templateName", parameter));
    } else {
        assertThrows(expectedException, () -> validator.validate("templateName", parameter));
    }
}

static Stream<Arguments> provideParameters() {
    return Stream.of(
        // String type parameters
        Arguments.of("validString", null),          // valid String
        Arguments.of(null, NullPointerException.class), // null String
        // CtTypeReference type parameters  
        Arguments.of(Mockito.mock(CtTypeReference.class), null),  // valid ref
        Arguments.of(null, NullPointerException.class)            // null ref
    );
}
```

### Incorrect example (testing only String type):
```java
@Test
void testValidateWithStringOnly() {
    assertDoesNotThrow(() -> validator.validate("templateName", "validString"));
    assertThrows(NullPointerException.class, () -> validator.validate("templateName", null));
    // Missing: CtTypeReference<?> tests - the null check might be missing for this type!
}
```