---
name: overridden-method-visibility-in-getAllMethods
description: When testing methods that collect/return inherited methods from class
  hierarchies, the TG should verify that when a child class re-declares a method from
  a parent, the parent's version is not included in results. Applies to getAllMethods()-style
  reflection that walks superclass chains.
code_tags:
- STATE_MUTATION
- INHERITANCE_VISIBILITY
test_pattern: STATE_TEST
---

# overridden-method-visibility-in-getAllMethods

## Instructions

# Overridden Method Visibility in getAllMethods

## Instructions

- WHEN the TG encounters a method that collects all methods/procedures from a class hierarchy (walking superclasses), such as `getAllMethods()` that gathers methods from the current type and its supertypes
- THEN the TG should test that when a child class overrides/re-declares a method with the **same signature** as a method in a parent class, only the child's version appears in the result set — the parent's hidden version must NOT be included
  - Create a parent class `Parent` with a method `void foo()`
  - Create a child class `Child extends Parent` that re-declares `void foo()` (same name, same return type, same parameter list)
  - Call `getAllMethods()` on the `Child` type
  - Verify the result contains exactly **one** method named `foo` — the child's version, not the parent's
- Expect that on the buggy version, the result incorrectly includes both the child's `foo` AND the parent's `foo` (or returns the parent's version alone)
- Common pitfalls:
  - ❌ Testing only a single class without an inheritance hierarchy (won't catch this bug)
  - ❌ Using methods with different signatures in parent and child (no override — both should appear)
  - ❌ Only checking that `getAllMethods()` returns methods at all, without verifying duplicate removal
  - ❌ Assuming method identity is compared by reference/object equality rather than by name + parameter signature

Example **correct** test pattern:
```java
// Parent has foo()
// Child extends Parent and also has foo() (overrides)
CtType<?> childType = factory.Type().get(Child.class);
Set<CtMethod<?>> methods = childType.getAllMethods();
// Should contain exactly one foo() — the child's
long fooCount = methods.stream().filter(m -> m.getSimpleName().equals("foo")).count();
assertEquals("Overridden method should not appear twice", 1, fooCount);
```

Example **incorrect** (won't catch the bug):
```java
CtType<?> type = factory.Type().get(SomeClass.class);
Set<CtMethod<?>> methods = type.getAllMethods();
assertFalse(methods.isEmpty()); // Passes even with the bug
```