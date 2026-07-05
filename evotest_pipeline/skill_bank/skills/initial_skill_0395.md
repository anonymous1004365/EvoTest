---
name: type-pool-method-description-resolution
description: When resolving method descriptions from a type pool, the resolution logic
  may incorrectly match or delegate between lazily-loaded type representations and
  eagerly-resolved ones, causing wrong method targets to be selected. Use this skill
  to test type pool resolution scenarios with mixed type representations.
code_tags:
- TYPE_CONVERSION
test_pattern: INTERACTION_TEST
---

# type-pool-method-description-resolution

## Instructions

# Type Pool Method Description Resolution

## Instructions

- WHEN the TG encounters code that resolves method descriptions by matching parameter types against a type pool's lazily-loaded type representations (e.g., `TypePool.Resolution` vs `TypeDescription`), and the matching logic involves comparing or converting between different type representation layers
- THEN the TG should write tests that specifically exercise the resolution path with a mix of:
  - Methods that are **invoked on instances** (non-static, requiring an instance target)
  - Static methods that a limited-view resolution might incorrectly match as instance-invocable
  - Type representations where a lazy `TypePool.Resolution` is used where an eager `TypeDescription` is expected, or vice versa
- The test should verify that when calling a method through a resolution mechanism (like `MethodCall.invoke(...).onMethod(...)`), the correct method is selected based on its **actual modifier** (static vs. instance), not just its parameter types
- **Concrete example from the bug**: A test like `testInstanceCallFromStaticMethod` should:
  1. Create a class with a static method (e.g., `static void foo()`) and another instance method (e.g., `void bar()`) 
  2. Use a type pool to resolve the static method's description
  3. Attempt to invoke it as an instance method (e.g., via `MethodCall.invoke(staticMethod).onMethod(instance)`)
  4. Verify that the resolution correctly identifies the method as static and either throws an appropriate exception (e.g., `IllegalArgumentException`) or delegates to the correct behavior
- **Common pitfalls**:
  - Testing only with instance methods or only with static methods — mix both
  - Assuming that type pool resolution always returns the same type representation — test with lazy vs. eager resolutions
  - Not testing the case where a method matches by name/parameters but has incompatible modifiers
  - Not including both the buggy (wrong resolution) and fixed (correct resolution) expectations

### Correct test approach
```java
@Test
public void testInstanceCallFromStaticMethod() {
    // Create a type with a static method
    // Resolve it via type pool
    // Attempt to invoke as instance method
    // Expect: exception or correct delegation
}
```

### Incorrect test approach
```java
@Test
public void testMethodCall() {
    // Only testing instance method calls
    // Not testing the static-vs-instance resolution edge case
    // Missing the mixed type representation scenario
}
```