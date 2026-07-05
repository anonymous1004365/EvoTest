---
name: template-parameter-type-validation
description: When method parameters accept both String and CtTypeReference types (or other heterogeneous types), test with all valid types to ensure proper type-specific handling. This skill prevents bugs where a handler only processes one type and erroneously calls methods on another type.
code_tags: ['FILE_CHANNEL_OPERATIONS', 'STATE_MUTATION', 'BOUNDARY_CHECK', 'TYPE_CONVERSION', 'NULL_CHECK', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that accepts parameters of multiple different types (e.g., `String` and `CtTypeReference`) and delegates to type-specific handling logic (e.g., a `forString` vs `forType` method or different constructor invocations based on the type)
  - THEN the TG should write tests that pass each distinct type as input, verifying the correct handler is invoked and no exception is thrown
  - For `CtTypeReference` type parameters, ensure the test creates a proper `CtTypeReference` instance (not a `String`) and verifies that the method does not mistakenly call `String`-only methods (like `substring`, `length`, `startsWith`, etc.) on it, which would cause a `ClassCastException` or `NoSuchMethodError`
  - Include concrete test cases such as:
    - Passing a plain `String` value and verifying correct behavior
    - Passing a `CtTypeReference` object (e.g., `factory.Type().create("java.lang.String")`) and verifying correct behavior
    - If the method is a setter/additional-parameters method, verify no `ClassCastException`, `NullPointerException`, or unexpected `NullPointerException` is thrown
  - Common pitfalls to avoid:
    - Testing only with `String` parameters (the most common usage) and assuming non-String types will also work
    - Forgetting that `CtTypeReference` may contain a `String`-like `toString()` representation, but is not itself a `String` — calling `String` methods on it will throw a `ClassCastException` at runtime
    - Not creating realistic `CtTypeReference` instances; use the appropriate factory method (e.g., `factory.Type().create(...)`) to construct test inputs

## Example

**Correct test** (catches the bug):
```java
@Test
public void testAddTemplateParameterWithTypeReference() {
    // Setup a CtTypeReference parameter
    CtTypeReference typeRef = factory.Type().create("java.lang.String");
    
    // Add it as a template parameter — this must not throw ClassCastException
    template.setAdditionalTemplateParameter(typeRef, "value");
    
    // Verify it was added correctly (no exception is the key assertion)
    assertTrue(template.getAdditionalTemplateParameters().containsKey(typeRef));
}
```

**Incorrect test** (misses the bug):
```java
@Test
public void testAddTemplateParameterWithString() {
    // Only tests String type — misses the bug entirely
    template.setAdditionalTemplateParameter("name", "value");
    assertEquals("value", template.getAdditionalTemplateParameters().get("name"));
}
```