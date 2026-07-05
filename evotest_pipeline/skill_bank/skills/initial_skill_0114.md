---
name: template-parameter-type-validation
description: When validating parameters in a template-based or generic proxy/bean construction, the TG should test that both typed (CtTypeReference, Class<?>) and primitive/wrapper types are correctly handled. This skill applies to any method that iterates over generic parameter types and validates them.
code_tags: ['ARGUMENT_VALIDATION', 'BOUNDARY_CHECK', 'STATE_MUTATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that iterates over a collection/array of generic parameter types (e.g., `CtTypeReference<?>[]`, `Class<?>[]`, `Type[]`) and validates or processes them (e.g., checking for null, checking assignability, or extracting simple names)
- THEN the TG should write a parametric test that passes **at least two kinds of type arguments**: (1) a primitive/wrapper type (e.g., `int.class`, `Integer.class`, or a `CtTypeReference` wrapping `int`/`Integer`) and (2) a complex/bean type (e.g., `String.class`, `List.class`, or a `CtTypeReference` wrapping those). Verify that both kinds are correctly processed without throwing an exception or returning unexpected results.
- Common pitfalls: 
  - Testing only `String` type parameters and assuming all types work the same way
  - Not testing primitive types (e.g., `int`, `long`, `boolean`) which may have different class representations (e.g., `Integer.TYPE` vs `Integer.class`)
  - Not testing null or empty parameter arrays, which may expose missing null checks
  - Assuming the validation logic handles all types uniformly without testing edge cases like arrays (`int[].class`), void (`void.class`), or varargs patterns

### Correct example (parametric test with multiple type kinds):
```java
@ParameterizedTest
@ValueSource(classes = {int.class, String.class, List.class, void.class, int[].class})
void testValidateParameterTypes(Class<?> paramType) {
    // Build a method/constructor with the given parameter type
    CtClass<?> ctClass = ...;
    CtMethod<?> method = ctClass.addMethod("public void foo(" + paramType.getSimpleName() + " x) {}");
    
    // Act & Assert: validation should not throw for any of these types
    assertDoesNotThrow(() -> validator.validate(method));
}
```

### Incorrect example (testing only one type):
```java
@Test
void testValidateParameterTypes() {
    // Only tests String — misses primitive types
    CtClass<?> ctClass = ...;
    CtMethod<?> method = ctClass.addMethod("public void foo(String x) {}");
    assertDoesNotThrow(() -> validator.validate(method));
    // Bug: int, long, boolean parameters would fail validation
}
```