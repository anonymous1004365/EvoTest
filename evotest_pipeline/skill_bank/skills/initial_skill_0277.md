---
name: constructor-call-explicit-type-argument
description: When writing tests for code that creates or processes constructor calls
  with generic type arguments, the TG should verify that explicit type arguments on
  constructor invocations are preserved and correctly used to determine the actual
  constructor type, not ignored or replaced with default values.
code_tags:
- STATE_MUTATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# constructor-call-explicit-type-argument

## Instructions

# Constructor Call Explicit Type Argument Preservation

## Instructions

- WHEN the TG encounters code that creates a `CtConstructorCall` (e.g., via `Factory.createConstructorCall()`) with generic type arguments (e.g., `new SomeType<T>()`) and then accesses the `actualClass` or `type` of that constructor call
- THEN the TG should write a test that:
  1. Creates a constructor call with one or more explicit type arguments (e.g., using `factory.Core().createConstructorCall()` or similar API)
  2. Calls the method that processes the constructor call to determine its target type
  3. Asserts that the determined type correctly reflects the explicit type argument(s) provided (e.g., `String.class` vs `Object.class`)
  4. On the buggy version, the test should fail because the constructor call's type argument is ignored, replaced, or mishandled

- Common pitfalls to avoid:
  - **Testing only with no type arguments**: A constructor call like `new Foo()` without generic type arguments may pass even on the buggy version. Always include explicit type arguments in at least one test case.
  - **Testing only the creation without asserting the type**: Just creating a constructor call is insufficient. The test must assert what `actualClass` or `getType()` returns, or assert behavior that depends on the correct type resolution.
  - **Assuming type arguments are always propagated**: Do not assume that setting type arguments on a constructor call automatically flows through to `actualClass` resolution without testing it explicitly.

### Example (Correct Test Approach)

```java
// BUGGY version: This test FAILS because type arguments on constructor calls
// are not used to determine actualClass
@Test
public void testConstructorCallWithExplicitTypeArgument() {
    // Create a constructor call with explicit type argument <String>
    CtConstructorCall<?> constructorCall = factory.Core().createConstructorCall();
    constructorCall.setType(factory.Type().createReference(
        factory.Type().createReference(String.class)));
    
    // Act: resolve the actual class from the constructor call
    // (e.g., by calling the method under test that processes it)
    CtTypeReference<?> actualClass = someProcessor.resolveConstructorActualClass(constructorCall);
    
    // Assert: should be String, not Object
    assertEquals("java.lang.String", actualClass.getQualifiedName());
}
```

### Example (Incorrect Test Approach)

```java
// INCORRECT: This test would PASS even on the buggy version,
// failing to catch the bug
@Test
public void testConstructorCallWithoutGenerics() {
    // No generic type argument — works on both versions
    CtConstructorCall<?> constructorCall = factory.Core().createConstructorCall();
    constructorCall.setSimpleName("Foo");
    
    // Only checking simple name, not the resolved type
    assertEquals("Foo", constructorCall.getSimpleName());
}
```