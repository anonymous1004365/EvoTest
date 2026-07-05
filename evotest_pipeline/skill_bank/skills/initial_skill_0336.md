---
name: method-reference-generic-type-validation
description: When testing methods that handle method references or lambda expressions
  with generic return types in Spoon, ensure both raw types and parameterized types
  are validated to prevent ClassCastException during compilation.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- COLLECTION_ITERATION
- TYPE_CONVERSION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# method-reference-generic-type-validation

## Instructions

# Method Reference Generic Type Validation

## Instructions

- WHEN the TG encounters code that retrieves a method reference's executable or attempts to get the generic return type of a `CtTypeReference` (e.g., `getActualClass()`, `getExecutable()`, `getGenericMethodFromReference()`)
- THEN the TG should test that retrieving the generic type from a method reference works correctly for both parameterized types (e.g., `List<String>`) AND raw generic method types
- Specifically, in Spoon's `MethodReferenceTest`, test `getGenericMethodFromReference()` by asserting that:
  1. A method reference to a generic method (e.g., `List::of`) returns the correct `CtTypeReference` with proper generic type parameters
  2. The returned `CtTypeReference` when calling methods like `getActualClass()` returns the correct class (e.g., `List.class` for `List::of`)
  3. The reference resolves without throwing a `ClassCastException` when compiled/processed
- Common pitfalls to avoid:
  - Testing only with non-generic method references (e.g., `String::valueOf`)
  - Testing only with raw types without generic parameters
  - Not verifying that the `CtTypeReference` correctly represents the declaring type's generics
  - Assuming `getActualClass()` always returns the right class without testing edge cases like generic methods with bounds

### Correct Example (what the TG should do):
```java
// In MethodReferenceTest
@Test
public void testGetGenericMethodFromReference() {
    // Create a factory with the right environment
    Launcher launcher = new Launcher();
    CtClass<?> type = launcher.getFactory().Class().get(SomeClassWithMethodReference.class);
    // ... find and test method references with generic declaring types (e.g., List::of, Map::of)
    CtMethodReference<?> ref = ...; // get the method reference
    CtTypeReference<?> declaringRef = ref.getDeclaringTypeReference();
    // Verify the type is correct (e.g., List for List::of)
    assertEquals(List.class, declaringRef.getActualClass());
    // Verify generics are preserved correctly
    assertNotNull(declaringRef.getActualTypeArguments());
}
```

### Incorrect Example (what the TG might do without this skill):
```java
// WRONG: Only testing with String::valueOf which has no generic declaring type
@Test
public void testGetGenericMethodFromReference() {
    // Only testing simple cases, missing generic method references
    // that could cause ClassCastException due to raw type mismatch
}
```