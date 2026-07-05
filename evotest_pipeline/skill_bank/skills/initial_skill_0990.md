---
name: typed-generic-parameter-access-path-validation
description: When validating access paths that involve typed/generic parameters (e.g.,
  CtTypeReference), test with both the concrete type (e.g., String) and the generic
  type reference itself as the parameter type, because the access path resolution
  may incorrectly handle cases where a typed parameter is used as a field's parameter
  type instead of a simple type.
code_tags:
- TYPE_CONVERSION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# typed-generic-parameter-access-path-validation

## Instructions

# Typed Generic Parameter Access Path Validation

## Instructions

- WHEN the TG encounters code that resolves access paths for fields or methods that involve type parameters (e.g., generic types like `CtTypedElement` with parameterized types), and the resolution logic distinguishes between "simple" type usage and "typed parameter" usage
- THEN the TG should create a test that exercises the access path resolution with both:
  1. A field whose type is a simple concrete type (e.g., `String`)
  2. A field whose type is a generic/typed parameter reference (e.g., `CtTypeReference<...>` or a parameterized type)
  - The test should verify that the access path correctly handles the case where a typed parameter is used as a field's type in a nested access expression (e.g., `a.b().c()` where `b()` returns a typed element)
  - Expect that the buggy version may produce incorrect access paths (e.g., generating `a.b.c` instead of the correct `a.b().c`), causing compilation errors or missing imports
- Common pitfalls:
  - Testing only with simple types like `String` or `int`, which pass but miss the bug
  - Not verifying the generated access path string or the resulting imports/compilation
  - Assuming that type parameters in the return type of a method don't affect access path resolution

### Example (Correct test approach)

```java
// Given two classes where one has a typed parameter field:
// class A {
//     CtTypeReference<String> ref;
// }
// class B {
//     A getA() { ... }
// }
// Test: verify that accessing b.getA().ref generates "b.getA().ref" (not "b.getA.ref")
CtTypeReference<String> typedRef = ...;
A a = new A();
a.ref = typedRef;
B b = new B();
// Verify the access path for b.getA().ref includes the method call parentheses
assertEquals("b.getA().ref", computeAccessPath(b, "ref"));
```

### Example (Incorrect test approach)

```java
// WRONG: Only tests with simple type fields
// class A {
//     String name;
// }
// class B {
//     A getA() { ... }
// }
// Test:
A a = new A();
a.name = "test";
B b = new B();
// This passes even in buggy version because simple types aren't affected
String accessPath = computeAccessPath(b, "name");
assertEquals("b.getA().name", accessPath); // PASSES in both buggy and fixed
// But the bug is only triggered when the field type is a typed parameter reference!
```