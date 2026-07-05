---
name: static-import-same-name-collision
description: This skill addresses static import resolution bugs where two different
  classes with the same simple name define static methods that share the same method
  name. When importing a static method via import static FullyQualifiedA.methodName,
  the compiler may resolve the wrong method if the other class is also imported or
  visible. The TG should detect this by verifying that static method references do
  not accidentally invoke the static method from a different class sharing the same
  name.
code_tags:
- VALIDATION
- STATIC_IMPORT_RESOLUTION
- IMPORT_COLLISION
test_pattern: STATE_TEST
---

# static-import-same-name-collision

## Instructions

# Static Import Same-Name Class Collision

## Instructions

- WHEN the TG encounters code that defines static methods on classes with the same simple name (e.g., `org.example.A.statMethod()` and `org.other.A.statMethod()`)
- AND the code performs static imports, reflection, or name-based resolution using just the simple class name
- THEN the TG should write a test that uses BOTH the target class and the colliding class in the same scope to verify that invoking the static method resolves to the correct class, not the wrong one
- Specifically, verify that calling the static method on the expected class produces the correct result/value, and that the same call on a different class with the same simple name doesn't interfere (e.g., produce a different result or shadow the expected one)
- Include test cases where both classes are imported/visible simultaneously and where the static method is referenced by simple name (which the compiler resolves based on import order or implicit shadowing)
- Use exact string/result comparisons to confirm the right static method from the right class was invoked
- Common pitfall: testing only with a single class imported, missing the collision scenario
- Another pitfall: assuming the compiler always picks the right overload — the bug often arises when the second class's static method shadows the first due to name resolution ordering

### Example (correct):
```java
// Given: Class A (from package p1) has static method foo() returning "p1.A"
// Given: Class A (from package p2) has static method foo() returning "p2.A"
// When both packages are imported:
import p1.A;
import p2.A;
// The test should explicitly qualify:
assertEquals("p1.A", p1.A.foo());
assertEquals("p2.A", p2.A.foo());
// And verify that unqualified simple name resolution does not
// accidentally invoke the wrong one.
```

### Example (incorrect — misses the bug):
```java
// Only tests one class, never sets up the collision
assertEquals("p1.A", A.foo()); // Might pass in isolation, fails when both classes are visible
```