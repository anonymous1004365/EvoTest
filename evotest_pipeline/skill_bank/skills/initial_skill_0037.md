---
name: method-reference-super-executable-type-check
description: When testing method references with super executable calls where the
  declaring type may be generic, this skill teaches how to verify that type references
  are correctly resolved and compared. Use when analyzing method reference resolution
  in code generation or reflection tools.
code_tags:
- STRING_PARSING
- ARGUMENT_VALIDATION
- NULL_CHECK
- TYPE_REFERENCE_EQUALS
- INHERITANCE_CHECK
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# method-reference-super-executable-type-check

## Instructions

# Method Reference Super Executable Type Check

## Instructions

- WHEN the TG encounters a method reference that involves a super executable call (e.g., `super::method`) where the declaring type of the method is a type variable or generic type (e.g., `T extends SomeClass`), and the code compares `CtTypeReference` objects for equality or uses them in resolution logic
- THEN the TG should test that the type reference comparison correctly handles type variables vs their concrete bound types. Specifically, when the declaring type of a super executable is a type variable (e.g., `T`) and a concrete type reference (e.g., `SomeClass`) is expected, the comparison should NOT produce a false negative due to type mismatch between the type variable reference and the bound type reference.

- WHEN the TG encounters a method reference resolution that filters or selects executables based on the declaring type of a super method (e.g., using `getAllExecutables()` and then filtering by declaring type)
- THEN the TG should test with both a direct superclass method reference and a generic superclass method reference to ensure that the type of the declaring executable is correctly resolved to the bound type, not the type variable.

- WHEN writing tests for method reference resolution with super executable calls
- THEN the TG should include a test case where:
  1. A class extends a generic superclass (e.g., `class Foo extends AbstractBar<String>`)
  2. A method reference to `super::someMethod` is used
  3. The test verifies that the resolved method reference's declaring type is the concrete bound (e.g., `AbstractBar<String>` or `AbstractBar`), not the type variable `T`
  4. If a `ClassNotFoundException` or similar exception occurs on the buggy version, the test should expect that exception

- Common pitfalls:
  - Testing only method references without generic superclasses (non-generic inheritance works but generic may not)
  - Comparing type references using `equals()` without considering that type variable references and their bound type references are different objects
  - Assuming that `getAllExecutables()` returns proper type information for super method references in generic contexts
  - Not testing the no-classpath (binary-only) mode where type resolution may differ

- Example (correct):
```java
// Test that super::method reference resolves correctly with generic superclass
abstract class AbstractBar<T> {
    void someMethod(T param) {}
}
class ConcreteBar extends AbstractBar<String> {
    void test() {
        Runnable r = super::someMethod; // method reference to super's generic method
    }
}
// Verify that CtMethodReference of someMethod has declaring type = AbstractBar (not T)
```

- Example (incorrect - would miss the bug):
```java
// Only test non-generic superclass method references
class Parent {
    void method() {}
}
class Child extends Parent {
    void test() {
        Runnable r = super::method;
    }
}
// This passes even if the generic case is broken
```