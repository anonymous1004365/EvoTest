---
name: null-safe-equality-for-entity-type-lookup
description: Use this skill when a method compares entity types using getJavaType()
  which can return null for non-entity managed types (e.g., java.lang.Object). It
  teaches how to write tests that pass both entity types and non-entity types to ensure
  null-safe equality checks.
code_tags:
- BUGGY_GETJAVATYPE_SKIPSENTITYTYPESWITHOUTJAVATYPE
- NULL_SAFE_EQUALS
- TYPE_MISMATCH
test_pattern: PARAMETRIC_TEST
---

# null-safe-equality-for-entity-type-lookup

## Instructions

# Null-Safe Equality for Entity Type Lookup

## Instructions

- WHEN the TG encounters a method that uses `javax.persistence.metamodel.EntityType` and calls `getJavaType()` on a managed type (e.g., `type.getJavaType()`) to compare it against a given `Class<?>` parameter (e.g., `type.getJavaType().equals(javaType)`)
- THEN the TG should test with BOTH an entity type that has a valid Java type AND a non-entity managed type (like `java.lang.Object`) that causes `getJavaType()` to return `null`, ensuring the comparison handles null safely
- Specifically, WHEN a method iterates over `metamodel.getManagedTypes()` and performs `type.getJavaType().equals(someClass)` or `someClass.equals(type.getJavaType())`, THEN the TG should create a test that includes a managed type whose `getJavaType()` returns `null` (e.g., `java.lang.Object` type) and verify the method does NOT throw a `NullPointerException`
- The TG must verify that for entity types (`EntityType`) the comparison works correctly, while for non-entity managed types (types that are not `EntityType` instances) the method skips them without error
- Common pitfalls: testing only with entity types that have valid Java types, or using `Objects.equals()` comparison that already handles null correctly but not checking whether the method correctly skips non-entity types entirely; also, failing to verify that the method correctly handles a `null` return from `getJavaType()` without crashing

### Example (correct test approach):

```java
@Test
void skipsEntityTypesWithoutJavaTypeForIdentifierLookup() {
    // Create a mock managed type that is NOT an EntityType and has getJavaType() returning null
    ManagedType<Object> managedType = mock(ManagedType.class);
    when(managedType.getJavaType()).thenReturn(null);
    
    // Create an EntityType mock that has a valid java type
    EntityType<SomeEntity> entityType = mock(EntityType.class);
    when(entityType.getJavaType()).thenReturn(SomeEntity.class);
    
    // Register both in the metamodel
    when(metamodel.getManagedTypes()).thenReturn(Set.of(managedType, entityType));
    
    // The method under test should NOT throw when iterating over managed types
    assertDoesNotThrow(() -> jpaMetamodel.isSingleIdAttribute(
        SomeEntity.class, "id", SomeIdClass.class));
    
    // The method should only find the identifier for the actual entity type
    assertTrue(jpaMetamodel.isSingleIdAttribute(
        SomeEntity.class, "id", SomeIdClass.class));
}
```

### Example (incorrect test approach - missing null-safe check):

```java
// BAD: Only tests with entity types that have valid java types
// This would NOT catch the NPE when getJavaType() returns null
@Test
void isSingleIdAttribute_withEntityTypesOnly() {
    EntityType<SomeEntity> entityType = mock(EntityType.class);
    when(entityType.getJavaType()).thenReturn(SomeEntity.class);
    when(metamodel.getManagedTypes()).thenReturn(Set.of(entityType));
    
    // This passes but doesn't test for the null case
    assertTrue(jpaMetamodel.isSingleIdAttribute(SomeEntity.class, "id", null));
}
```