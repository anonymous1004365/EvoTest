---
name: template-parameter-type-validation
description: When injecting or validating proxy template parameters, the type of each value must match the declared CtTypeReference. A bug occurs when only String types are tested but the code accepts the parameter without verifying actual type compatibility — always test with non-String types like CtTypeReference objects. Use this skill to catch cases where loose typing lets incompatible parameters silently pass through.
code_tags: ['VALIDATION', 'BOUNDARY_CHECK', 'STATE_MUTATION', 'ELEMENT_TYPE_MISMATCH']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that processes template parameters (e.g., a proxy class like `TemplateParameterProxy`), where parameters are passed via methods such as `setAddParam(String, Object)` or `addParam(String, Object)`, and values are stored in a collection like a `List<Object>` or `Map<String, Object>`
- THEN the TG should test that parameters with non-String types (specifically `CtTypeReference<?>` objects) are properly handled. The test should:
  1. Create a `CtTypeReference<?>` instance representing a valid type (e.g., using `factory.Type().createReference(String.class)`)
  2. Add the template parameter using the parameter-setting method with a key-value pair where the value is the `CtTypeReference` object
  3. Verify that the parameter was correctly stored and retrievable with its expected type (not coerced, cast, or silently dropped)

- WHEN validating parameter consumption, the TG should check that parameters with different types are correctly distinguished and that no `ClassCastException` occurs when the parameter value is accessed.

- Be concrete: The value being passed is a `CtTypeReference<?>` object (from `spoon.reflect.factory.TypeFactory`), and the method being tested is typically called with a name like `setAddParam` or `addParam`.

- Common pitfalls to avoid:
  - Testing only with `String` type parameters — this misses the bug because the bug only manifests when non-String types are passed (e.g., `CtTypeReference`, `Integer`, custom objects)
  - Assuming that because a method accepts `Object`, any value type works correctly — the bug is that the parameter may not be stored or retrieved correctly for non-String types
  - Not asserting both the key existence AND value type after retrieval

### Example (Correct Test)

```java
// Correct: Tests with a non-String type (CtTypeReference)
@Test
public void testTemplateParameterWithCtTypeReference() {
    // Given
    TemplateParameterProxy proxy = new TemplateParameterProxy();
    CtTypeReference<?> typeRef = factory.Type().createReference(String.class);
    
    // When
    proxy.setAddParam("myType", typeRef);
    
    // Then
    // Verify no exception, and that the parameter can be retrieved
    // with the correct type
    Object retrieved = proxy.getParam("myType");
    assertNotNull(retrieved);
    assertTrue(retrieved instanceof CtTypeReference);
    assertEquals(String.class.getName(), ((CtTypeReference<?>) retrieved).getQualifiedName());
}
```

### Example (Incorrect Test — Misses the Bug)

```java
// WRONG: Only tests with String value — misses the bug
@Test
public void testTemplateParameterWithStringOnly() {
    TemplateParameterProxy proxy = new TemplateParameterProxy();
    proxy.setAddParam("myParam", "hello");
    
    Object retrieved = proxy.getParam("myParam");
    assertEquals("hello", retrieved);  // Passes even on buggy version
}
```