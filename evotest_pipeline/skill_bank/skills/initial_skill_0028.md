---
name: template-parameter-type-validation
description: Teaches the TG to validate proxy template parameters by testing with multiple distinct type variants (String, CtTypeReference, etc.) to catch incorrect type equality checks when matching template parameters against class fields.
code_tags: ['NULL_CHECK', 'BOUNDARY_CHECK', 'VALIDATION', 'TYPE_HIERARCHY_CHECK', 'TYPE_REFERENCE_EQUALS']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that iterates over template parameters (e.g., `getTemplateParameters()` or similar) and tries to match them against fields of a class using equality checks (`.equals()`, `.contains()`, or `==`),
- THEN the TG MUST write a parameterized test that passes different **type variants** for the same conceptual template parameter. Specifically:
  1. Use a **plain `String`** value as one test case.
  2. Use a **`CtTypeReference`** (or the framework's equivalent typed reference) as another test case, where the type reference wraps the same string value.
  3. Verify that both variants are handled identically by the method under test. The test should assert that the method processes both variants the same way (e.g., both match the same field, or both throw the same exception).
- Common pitfalls:
  - ❌ Testing only with `String` type parameters. The bug often arises because `.equals()` or `.hashCode()` between `String` and `CtTypeReference` returns `false` even when they represent the same type, so testing only one type misses the bug.
  - ❌ Assuming that because two objects are "conceptually equal" they will compare equal via `.equals()`. Always test both variants explicitly.
  - ❌ Not testing the **actual field matching logic** — the TG should verify that the parameter is correctly matched to a class field, not just that no exception is thrown.

### Correct Example (catches the bug)
```java
@Test
public void testPersistMetaNoneDataAddAbstractEntityType() {
    // Arrange
    when(entityType.getClassName()).thenReturn("TestEntity");
    when(entityType.getAbstract()).thenReturn(true);
    
    // Test with String template parameter
    EntityType entityTypeWithStringParam = mock(EntityType.class);
    when(entityTypeWithStringParam.getClassName()).thenReturn("TestEntity");
    when(entityTypeWithStringParam.getAbstract()).thenReturn(true);
    when(entityTypeWithStringParam.getTemplateParameters()).thenReturn(Collections.singletonList("param"));
    
    // Test with CtTypeReference template parameter
    EntityType entityTypeWithRefParam = mock(EntityType.class);
    when(entityTypeWithRefParam.getClassName()).thenReturn("TestEntity");
    when(entityTypeWithRefParam.getAbstract()).thenReturn(true);
    when(entityTypeWithRefParam.getTemplateParameters()).thenReturn(Collections.singletonList(
        new CtTypeReferenceImpl("param")
    ));
    
    // Act & Assert - both should throw appropriate exception for abstract entity with template params
    assertThrows(SomeException.class, () -> persister.persist(entityTypeWithStringParam));
    assertThrows(SomeException.class, () -> persister.persist(entityTypeWithRefParam));
}
```

### Incorrect Example (misses the bug)
```java
@Test
public void testPersistMetaNoneDataAddAbstractEntityType() {
    // Only tests String parameters — misses the CtTypeReference bug entirely
    EntityType entityType = mock(EntityType.class);
    when(entityType.getClassName()).thenReturn("TestEntity");
    when(entityType.getAbstract()).thenReturn(true);
    when(entityType.getTemplateParameters()).thenReturn(Collections.singletonList("param"));
    
    assertThrows(SomeException.class, () -> persister.persist(entityType));
    // Test passes on buggy code, but the bug with CtTypeReference is never caught
}
```