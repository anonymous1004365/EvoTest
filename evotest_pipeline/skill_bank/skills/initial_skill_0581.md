---
name: cttype-hasmethod-null-declaringtype
description: When a CtType class has a method (e.g., hasMethod) that accesses getDeclaringType()
  without null-checking, the TG should test with types that have a null declaring
  type (e.g., top-level classes) to verify the method handles null gracefully instead
  of throwing NPE.
code_tags:
- VALIDATION
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# cttype-hasmethod-null-declaringtype

## Instructions

# Handling Null DeclaringType in CtType Reflection Methods

## Instructions

- **WHEN** the TG encounters a CtType-like class with methods that navigate the type hierarchy (e.g., `hasMethod`, `getDeclaringType`, or methods that chain-call on a potentially null type reference):
  - **THEN** the TG should write a test that creates a type instance (e.g., using a factory) where `getDeclaringType()` returns `null`, such as a top-level class, and then calls the hierarchy-dependent method on it.
  - **THEN** the test should verify that the method does NOT throw a `NullPointerException` when the declaring type is null.
  - **THEN** if the method is expected to search the declaring type's methods (e.g., `hasMethod` recursively looking at parent types), the test should verify correct behavior for both:
    1. Types with a non-null declaring type (e.g., nested/inner types) — these should traverse up and search the parent.
    2. Types with a null declaring type (e.g., top-level types) — these should short-circuit without traversal and return `false` (or handle gracefully).
  - **COMMON PITFALL**: Testing only inner/nested types that have a non-null declaring type, so the null path is never exercised. Always include a top-level type in the test.
  - **COMMON PITFALL**: Assuming `getDeclaringType()` will never return null. In reflective/type-system code, top-level types legitimately have no declaring type.

### Correct Example (should not throw NPE on buggy version)

```java
// Test a top-level class where getDeclaringType() returns null
@Test
public void testHasMethodOnTopLevelClass() {
    // Assuming a factory that creates a CtType with no parent
    CtType<?> topLevelType = spoon.reflect.factory.Factory.createClass("MyTopLevelClass");
    // hasMethod should handle null declaring type without NPE
    assertFalse(topLevelType.hasMethod("someMethod"));
}
```

### Incorrect Pattern (what the TG might write without this skill — only tests nested types)

```java
// INCORRECT: Only tests nested/inner types where declaring type is non-null
@Test
public void testHasMethodOnNestedClass() {
    CtClass<?> inner = factory.createClass("Outer$Inner");
    // This only tests the path where getDeclaringType() != null
    assertFalse(inner.hasMethod("someMethod"));
}
```