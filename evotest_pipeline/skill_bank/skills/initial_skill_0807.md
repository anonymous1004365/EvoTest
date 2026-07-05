---
name: parameter-reference-type-construction
description: When constructing parameter references in Spoon, always test that both
  String-typed parameter names and CtTypeReference-typed parameter types are properly
  accepted. The bug was that setType silently failed when passed a non-String argument
  due to an overload resolution issue.
code_tags:
- TYPE_CONVERSION
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# parameter-reference-type-construction

## Instructions

# Parameter Reference Type Construction in Spoon

## Instructions

WHEN the TG encounters code that constructs parameter references (e.g., `ParameterRef`, `VariableAccess`) and has a method like `setSimpleName(Object)` or similar overloaded setters that accept both `String` and other types like `CtTypeReference`:

- THEN the TG should write a **parametric test** that verifies the setter works correctly for BOTH `String` and non-String types (e.g., `CtTypeReference<?>`).
  
- Specifically, if there is a method like `setSimpleName(Object)` that delegates differently based on the argument type (e.g., `String` vs `CtTypeReference`), verify BOTH:
  1. Passing a `String` works correctly — the simple name is set to the string value.
  2. Passing a `CtTypeReference<?>` works correctly — the simple name should be extracted from the type reference (e.g., via `getSimpleName()` on the type reference).

- In Spoon, when calling `factory.createVariableAccess().setSimpleName(someCtTypeReference)`, the setter must NOT simply call `toString()` on the argument. Verify that the setter properly checks `if (o instanceof CtTypeReference)` and extracts the simple name from the type reference, rather than just using `o.toString()`.

- The test must construct both a `String` argument (e.g., `"foo"`) and a `CtTypeReference` argument (e.g., `factory.Type().createReference(String.class)`) and assert that both result in the same expected simple name (`"String"`).

- **Common pitfalls to avoid:**
  - Testing only with `String` arguments — this misses bugs in the non-String code path.
  - Assuming `toString()` provides the same result as `getSimpleName()` on a `CtTypeReference` — these can differ.
  - Not constructing a proper `CtTypeReference` via the factory (e.g., `factory.Type().createReference(...)`) for the test.
  - Using anonymous or mock objects instead of real `CtTypeReference` instances from the Spoon factory.

- **Example (correct test):**
```java
@Test
public void testParameterReferenceTypeConstruction() {
    SpoonAPI factory = new Launcher().createFactory();
    
    // Test with String
    CtVariableAccess<String> stringAccess = factory.createVariableAccess();
    stringAccess.setSimpleName("String");
    assertEquals("String", stringAccess.getSimpleName());
    
    // Test with CtTypeReference
    CtVariableAccess<?> typeAccess = factory.createVariableAccess();
    CtTypeReference<String> stringTypeRef = factory.Type().createReference(String.class);
    typeAccess.setSimpleName(stringTypeRef);
    assertEquals("String", typeAccess.getSimpleName());
}
```

- **Example (incorrect test — only tests String path):**
```java
@Test
public void testParameterReferenceTypeConstruction() {
    SpoonAPI factory = new Launcher().createFactory();
    CtVariableAccess<String> access = factory.createVariableAccess();
    access.setSimpleName("String");
    assertEquals("String", access.getSimpleName());
    // Missing: testing with CtTypeReference argument!
}
```