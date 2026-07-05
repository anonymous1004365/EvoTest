---
name: string-literal-template-type-validation
description: When validating template parameters in string literal methods, test that
  non-String types (like CtTypeReference) are not incorrectly treated as String parameters.
  This skill helps catch bugs where instanceof checks fail to properly distinguish
  between template parameter types.
code_tags:
- VALIDATION
- ARGUMENT_VALIDATION
- NULL_CHECK
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# string-literal-template-type-validation

## Instructions

# String Literal Template Type Validation

## Instructions

WHEN the TG encounters a method that processes template/placeholder parameters from string literals (e.g., `${...}` placeholders) and uses `instanceof` checks to distinguish between different parameter types (like `String` vs `CtTypeReference`):
- THEN the TG should write a parametric test that passes BOTH a `String` value AND a `CtTypeReference` value as template parameters, verifying that the method correctly handles each type.
- The test should verify that when the method encounters a placeholder that is NOT a simple type on the lefthand side of a dot expression, it does NOT incorrectly treat the method as having a String-typed template parameter.
- Use the exact types from the codebase: `CtTypeReference` for type references, and check that type arguments are resolved properly.
- Include negative test cases: test that type references (like `String.class`) are NOT interpreted as method calls with String template parameters.

Common pitfalls:
- Testing only with `String` type parameters when the method also handles `CtTypeReference` or other type instances.
- Assuming that all template parameters inside `${}` are plain strings without checking their actual type.
- Not verifying that `instanceof` checks on template parameter types distinguish between String and non-String types correctly.

Example (correct):
```java
// Verify that a type reference parameter is NOT treated as a String template param
CtTypeReference<?> typeRef = factory.Type().createReference(String.class);
result = snippetProcessor.processParameter(typeRef);
assertFalse(result.isStringParameter()); // should NOT be treated as String
assertTrue(result.isTypeReference()); // should be recognized as type ref
```

Example (incorrect):
```java
// WRONG: Only tests with String values
result = snippetProcessor.processParameter("someClass");
// Missing: test with CtTypeReference, which would have exposed the bug
```