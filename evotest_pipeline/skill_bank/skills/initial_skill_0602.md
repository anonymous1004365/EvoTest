---
name: constructor-parameter-type-mismatch
description: Helps detect bugs where constructor parameters for non-top-level classes
  (like inner, anonymous, or local classes) have their types incorrectly handled,
  especially when the constructor's declaring class differs from the enclosing class.
  Use this skill when testing code that introspects or builds constructor parameter
  types.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# constructor-parameter-type-mismatch

## Instructions

# Constructor Parameter Type Mismatch for Non-Top-Level Classes

## Instructions

- WHEN the TG encounters code that retrieves constructor parameter types for a non-top-level class (e.g., an inner class, anonymous class, or local class) using reflection or a reflection-based tree builder:
  - THEN the TG should verify that each constructor parameter's type is correctly resolved to the **expected type's canonical name**, not incorrectly inferred as the enclosing class or null.
  - The test should construct a class that has an **inner class with a constructor that takes annotated parameters** (e.g., a parameter with `@NotNull` or a custom annotation). The test should create an instance of the inner class and then assert that the constructor parameter types match what is expected by comparing against the actual parameter types of the inner class constructor.
  - For example: if a method like `getConstructorParamType(paramIndex)` is supposed to return `String.class`, the test should verify that `getConstructorParamType(0)` returns `String.class` and not `null` or the enclosing type.

- WHEN a reflection-based visitor or tree builder processes an inner class's constructor:
  - THEN the TG should test with multiple parameter types including **primitive types** (e.g., `int`, `boolean`), **reference types** (e.g., `String`, `List`), and **annotated parameters** to ensure the correct type is associated with the constructor, not mixed up with the outer class's constructor or lost due to missing null checks.

- Common pitfalls to avoid:
  - ❌ Testing only with top-level (non-inner) classes, missing the bug that only manifests with inner classes.
  - ❌ Testing only with unannotated constructor parameters, missing bugs caused by parameter annotations affecting type resolution.
  - ❌ Assuming the constructor parameter types are the same as the enclosing class's constructor parameter types.
  - ❌ Not asserting the exact type (e.g., `assertEquals(String.class, actualType)`) and instead just checking for non-null.
  - ❌ Not testing with classes that have multiple constructors to ensure the right constructor is picked.

### Correct example (what the TG should produce):
```java
// Test that the constructor of an inner class with annotated parameters
// correctly resolves its parameter types
@Test
public void testInnerClassConstructorParamTypes() {
    // Assume 'builder' is a JavaReflectionTreeBuilder-like object
    CtClass<?> innerClass = builder.build(InnerWithAnnotatedParam.class);
    CtConstructor<?> constructor = innerClass.getConstructors().get(0);
    List<CtParameter<?>> params = constructor.getParameters();
    
    // First parameter should be String (not null, not the enclosing type)
    assertEquals("java.lang.String", params.get(0).getType().getQualifiedName());
    // If there's a second parameter, verify it too
    assertEquals("int", params.get(1).getType().getQualifiedName());
}

// The inner class used in the test
static class InnerWithAnnotatedParam {
    public InnerWithAnnotatedParam(@NotNull String name, int value) {
        // constructor body
    }
}
```

### Incorrect example (what the TG might write without this skill):
```java
// Wrong: Only testing top-level class, missing the inner class bug
@Test
public void testConstructorParamTypes() {
    CtClass<?> clazz = builder.build(TopLevelClass.class);
    CtConstructor<?> constructor = clazz.getConstructors().get(0);
    // This passes for top-level but would NOT catch the bug
    assertNotNull(constructor.getParameters().get(0).getType());
}
```