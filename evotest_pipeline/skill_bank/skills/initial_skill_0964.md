---
name: abstract-override-resolution-validity
description: When testing code that resolves override relationships between methods
  in subclasses of abstract types, verify that the resolution handles cases where
  a subclass overrides a concrete method inherited from its abstract parent. Test
  with both direct overrides in the abstract class's immediate subclass and with multi-level
  inheritance chains.
code_tags:
- NULL_CHECK
- VALIDATION
- ABSTRACT_OVERRIDE_RESOLUTION
test_pattern: PARAMETRIC_TEST
---

# abstract-override-resolution-validity

## Instructions

# Abstract Override Resolution Validity

## Instructions

- WHEN the TG encounters code that resolves whether a method is overridden — such as traversing a class hierarchy to find the implementing method for a given declaration — THEN it should test with a class hierarchy where:
  1. An abstract class defines a concrete (non-abstract) method.
  2. A concrete subclass extends that abstract class and overrides the method.
  The test should verify that the override resolution correctly identifies that the method IS overridden in the subclass (i.e., the resolution does not incorrectly return the abstract class's method as the "nearest" implementation when a concrete subclass override exists).

- WHEN testing method override resolution across multi-level hierarchies, THEN include cases where:
  - The immediate superclass is abstract and provides a concrete method.
  - The concrete subclass overrides that method.
  Verify that the resolution does NOT traverse past the concrete subclass back to the abstract class's method.

- Common pitfalls:
  - Testing with only single-level inheritance (concrete parent → concrete child) misses the bug pattern.
  - Testing with only abstract methods (no concrete body in the abstract class) misses the bug pattern.
  - Assuming that if a parent class is abstract, its concrete methods are always overridden.
  - Only testing one type of inheritance depth (e.g., only checking immediate subclasses).

- Example (correct test):
  ```java
  // Given an abstract class with a concrete method
  abstract class AbstractParent {
      public String getName() { return "abstract"; }
  }
  // And a concrete subclass that overrides it
  class ConcreteChild extends AbstractParent {
      @Override
      public String getName() { return "concrete"; }
  }
  
  // When resolving which class provides the override for getName()
  // Then ConcreteChild should be identified as the overriding class
  Class<?> resolved = resolveOverride(ConcreteChild.class, "getName");
  assertEquals(ConcreteChild.class, resolved);
  // NOT AbstractParent.class
  ```

- Example (incorrect test that would pass buggy code):
  ```java
  // Only testing single-level concrete hierarchy (no abstract parent)
  class Parent { public String getName() { return "parent"; } }
  class Child extends Parent { @Override public String getName() { return "child"; } }
  
  Class<?> resolved = resolveOverride(Child.class, "getName");
  assertEquals(Child.class, resolved); // This test would pass even with the bug
  ```