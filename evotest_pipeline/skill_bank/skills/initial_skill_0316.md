---
name: wildcard-type-specialization-resolution
description: When a generic type uses wildcard bounds (? extends X), the ClassTypeInformation
  must resolve to the correct target type during specialization, not just the wildcard
  bound. Test with concrete subclasses to verify specialization resolves wildcards
  correctly.
code_tags:
- TYPE_CONVERSION
- NULL_CHECK
- VALIDATION
test_pattern: STATE_TEST
---

# wildcard-type-specialization-resolution

## Instructions

# Wildcard Type Specialization Resolution

## Instructions

**WHEN** the TG encounters code that resolves or specializes a generic type using wildcard bounds (e.g., `? extends SomeType`, `? super SomeType`), and the specialization produces a `ClassTypeInformation` instance:

- **THEN** the TG should write a test that:
  1. Creates a concrete subclass of the generic type parameter (e.g., `class SubClass extends SomeType` or uses an existing concrete implementation)
  2. Uses the type resolution mechanism to specialize a parent type that contains a wildcard-based type parameter bound to that concrete subclass
  3. Asserts that the resulting resolved type matches the **concrete subclass** type, not just the wildcard bound type
  4. Verifies that `getType()` on the resolved `ClassTypeInformation` returns the concrete subclass's `Class`, not the bound's class

**Common pitfalls to avoid:**
- Testing only with the wildcard bound type (e.g., `SomeType`) rather than a concrete subclass — this passes even on buggy code and misses the bug.
- Forgetting that wildcard `? extends T` should be resolved to the **actual** concrete type used, not just to `T`.
- Assuming `ClassTypeInformation` always resolves wildcards correctly — the bug shows it can fail when specialization is involved.

**Concrete example from the bug:**
- There is a type like `Container<? extends BaseType>` being specialized with a concrete subtype `ConcreteType extends BaseType`
- The buggy version resolves the wildcard to `BaseType` (the bound) instead of `ConcreteType` (the actual type argument)
- The fix ensures that during specialization, the actual concrete type argument is preserved through wildcard bounds

**Example test (correct):**
```java
// Given a generic container: class Container<T> { ClassTypeInformation<T> resolve() { ... } }
// And concrete types: interface Animal {} class Dog implements Animal {}

// Test specialization with wildcard
Container<? extends Animal> container = new Container<Dog>();
ClassTypeInformation<?> resolved = container.resolveSpecialization();
// Should resolve to Dog, not Animal
assertEquals(Dog.class, resolved.getType());
```

**Example test (incorrect — misses the bug):**
```java
// This test passes even on buggy code because it doesn't test the wildcard resolution
Container<Animal> container = new Container<Animal>();
ClassTypeInformation<?> resolved = container.resolveSpecialization();
assertEquals(Animal.class, resolved.getType()); // Always passes
```

**What the test must verify on the buggy version:**
The test should expect `Dog.class` (the concrete type), and on the buggy version it would return `Animal.class` (the wildcard bound), causing a test failure that correctly identifies the bug.