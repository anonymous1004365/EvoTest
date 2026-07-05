---
name: null-context-cast-type-creation
description: When a factory method creates a type reference by casting a null or resolving
  a null context, the TG must test that the method handles null input gracefully rather
  than throwing a NullPointerException.
code_tags:
- NULL_CHECK
- ARGUMENT_VALIDATION
test_pattern: EXCEPTION_TEST
---

# null-context-cast-type-creation

## Instructions

# Null Context Cast Type Creation

## Instructions

- WHEN the TG encounters a factory method (e.g., in `TypeFactory`) that creates a `CtTypeReference` by accepting a `Class<?>` parameter, potentially using `getSuperclass()` or similar methods that may return `null`, and that null is passed into a `createReference` method that does an internal cast
- THEN the TG MUST write a test that:
  1. Passes `null` explicitly as the `Class<?>` argument to the factory method
  2. Asserts that the method throws an appropriate exception (e.g., `NullPointerException` with a meaningful message, or `IllegalArgumentException`)
  3. If the factory method internally calls something like `factory.Type().createReference(someClass.getSuperclass())` where `getSuperclass()` can return null, tests that scenario specifically
- Include concrete examples: For a method like `TypeFactory.createTypeRef(Class<?> c)`, test with `typeFactory.createTypeRef(null)` and expect a `NullPointerException` or `IllegalArgumentException`
- Common pitfalls to avoid:
  - ❌ Testing only with non-null arguments and assuming the method works correctly with null
  - ❌ Catching `Exception` and passing the test — assert the specific expected exception type
  - ❌ Not testing intermediate null values (e.g., `getSuperclass()` returning null and being passed to another method)

### Correct Test Example
```java
@Test
public void testCreateTypeRefWithNull() {
    TypeFactory typeFactory = new TypeFactory();
    assertThrows(NullPointerException.class, () -> {
        typeFactory.createTypeRef(null);
    });
}
```

### Incorrect Test Example
```java
// ❌ Wrong: Only tests non-null input, missing the null edge case
@Test
public void testCreateTypeRef() {
    TypeFactory typeFactory = new TypeFactory();
    CtTypeReference<?> ref = typeFactory.createTypeRef(String.class);
    assertNotNull(ref);
}
```