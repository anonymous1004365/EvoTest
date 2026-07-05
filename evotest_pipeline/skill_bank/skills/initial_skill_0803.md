---
name: null-pointer-all-operators-validation
description: When detecting methods that iterate over operators or template parameters
  using reflection or collector patterns, test that all operator types (including
  non-String types) are handled correctly without throwing NullPointerException. This
  is critical when template parameters are resolved from internal structures that
  may contain non-String types.
code_tags:
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# null-pointer-all-operators-validation

## Instructions

# NullPointerException When Processing All Operators/Template Parameters

## Instructions

- WHEN the TG encounters code that iterates over operators, template parameters, or method arguments using a collector/visitor pattern that checks `instanceof String` or similar type guards
- THEN the TG should write a test that exercises the method with a representative set of ALL parameter/operator types, including both String and non-String types (e.g., `CtTypeReference`, `CtLiteral`, `CtBinaryOperator`), ensuring the method does not throw a NullPointerException
- Specifically, the test should verify that for ALL operators/template parameters (not just String ones), the method completes without throwing NPE — use `assertDoesNotThrow` or a try-catch pattern
- Common pitfalls:
  - Testing only String-type parameters (the "happy path") and missing the NPE that occurs on non-String types
  - Writing a test that only checks the first parameter type, or only checks one specific operator type
  - Not including the exact non-String types that trigger the bug (e.g., a `CtTypeReference` or a complex expression tree)
  - Assuming the method handles all types correctly without testing the specific non-String variant

### Correct Example (Java, JUnit 5)
```java
@Test
public void testNoNPEOnNonStringTemplateParameter() {
    // Arrange: create a method with a non-String template parameter (e.g., a CtTypeReference)
    CtMethod<?> method = ...; // Obtain via Spoon or factory
    // Act & Assert: should not throw NullPointerException
    assertDoesNotThrow(() -> myCollector.visitMethod(method));
}
```

### Incorrect Example
```java
@Test
public void testOnlyStringParam() {
    // Only tests String — misses the NPE bug entirely
    CtMethod<?> method = factory.createMethod(...); // with only String params
    myCollector.visitMethod(method); // passes, but doesn't prove safety
}
```