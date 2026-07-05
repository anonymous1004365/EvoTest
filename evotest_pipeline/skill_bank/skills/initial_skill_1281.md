---
name: template-import-type-mismatch-handling
description: When resolving template parameters or imports in Spoon, test that methods
  handling both String and CtTypeReference types correctly handle mismatches — catching
  ClassNotFoundException for type references while gracefully handling unexpected
  types.
code_tags:
- TYPE_CONVERSION
- VALIDATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# template-import-type-mismatch-handling

## Instructions

# Template Import Type Mismatch Handling

## Instructions

- WHEN the TG encounters code that resolves template parameters or imports using type information (e.g., `CtTypeReference` vs `String` parameters in methods like `resolve`, `getImport`, `processTemplateParameter`)
- THEN it should test both of the following scenarios:
  1. **String-type parameters**: Pass a valid String value (e.g., `"java.util.List"`) and verify the method returns the expected resolved type or import. This is the common happy path.
  2. **CtTypeReference-type parameters** (where applicable): Pass a `CtTypeReference` object (or another non-String type) and verify the method handles it correctly — either by resolving it or throwing a `ClassNotFoundException` for missing types.
- The test MUST verify **type-specific behavior**: When the method receives parameter types it cannot handle (e.g., passing a `CtTypeReference` to a method that only handles `String`, or vice versa), it should throw an appropriate exception (e.g., `ClassNotFoundException`, `ClassCastException`, or similar).
- **Common pitfalls to avoid**:
  - Testing only the `String` type parameter path and missing broken behavior for `CtTypeReference` or other type parameters.
  - Assuming all parameters are the same type without checking method signatures for type-specific dispatch.
  - Not verifying the exception/error message for type mismatches.
  - Mocking away the type resolution logic instead of exercising the actual dispatch code.

### Correct Example

```java
// Test that calls processTemplateParameter with both String and CtTypeReference
@Test
public void testImportResolutionWithBothTypes() {
    // Test String type parameter
    String result = importResolver.resolve("java.util.List");
    assertNotNull(result);
    assertEquals("java.util.List", result.getQualifiedName());

    // Test CtTypeReference type parameter (should fail on missing type)
    CtTypeReference ref = factory.Type().createReference("com.example.MissingClass");
    assertThrows(ClassNotFoundException.class, () -> {
        importResolver.resolve(ref);
    });
}
```

### Incorrect Example

```java
// BUG: Only tests String type, misses the CtTypeReference path
@Test
public void testImportResolution() {
    String result = importResolver.resolve("java.util.List");
    assertNotNull(result);
    // Missing: no test for CtTypeReference parameter type
}
```