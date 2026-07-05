---
name: template-parameter-type-validation
description: When code validates or registers template/type parameters (e.g., a Map of template types), the test generator should test with diverse parameter types including CtTypeReference and String. This skill catches bugs where a method accepts and stores different parameter types but only supports one type path during resolution.
code_tags: ['STATE_UPDATE_CONSISTENCY', 'STATE_MUTATION', 'NULL_CHECK', 'ARGUMENT_VALIDATION', 'TYPE_CONVERSION', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

WHEN the TG encounters code that maintains a mapping of template parameter names to values (e.g., `Map<String, Object>` where values can be either `String` class names or `CtTypeReference` type references), and the code resolves these parameters by name:

- THEN the TG should design a test that adds parameters of **different types** (both `String` and `CtTypeReference`) with the same parameter name and verifies that the resolution logic handles both correctly.
- Specifically, when a `CtTypeReference` value is stored, the test should verify that resolving the parameter returns a value of the expected type, not a `String`.
- Use the triggering test pattern: create a test class with an `@Test` method that:
  1. Gets or creates the template parameter container (e.g., a `CtType` or similar class with template parameter support).
  2. Adds template parameters using **both** `String` values and `CtTypeReference` values (e.g., via `addParameter(String, Object)` or `setParameter(...)`).
  3. For the `CtTypeReference` case, the test should verify that the resolved parameter is a proper `CtTypeReference` and not a bare `String`.
  4. Expect that on the buggy version, the resolution of `CtTypeReference` parameters may fail (e.g., returning `null` or returning a `String` instead of a `CtTypeReference`), while on the fixed version it should succeed.
- The test should also verify that `String`-type parameters still resolve correctly (regression check).

**Common pitfalls to avoid:**
- Testing only with `String` type parameter values — the bug manifests specifically with non-String types like `CtTypeReference`.
- Assuming that `Map.get(key)` returns the stored object without checking its type — the bug may involve conditional logic that only handles `String` instances.
- Not verifying that the returned value is of the correct expected type (e.g., using `assertEquals` on `toString()` instead of checking the actual object type).
- Overlooking the need to test parameter addition and resolution as two separate steps.

**Correct test approach (fixed version):**
```java
@Test
public void testParameterWithTypeReference() {
    CtType<?> type = factory.Type().get("MyType");
    CtTypeReference<?> ref = factory.Type().get("java.util.List").getReference();
    type.addParameter("T", ref);
    Object resolved = type.getParameter("T");
    assertTrue("Parameter value should be a CtTypeReference, not a String", 
               resolved instanceof CtTypeReference);
    assertEquals("java.util.List", resolved.toString());
}
```

**Incorrect test approach (misses the bug):**
```java
@Test
public void testParameterAdd() {
    CtType<?> type = factory.Type().get("MyType");
    type.addParameter("T", "java.util.List"); // Only tests String path
    Object resolved = type.getParameter("T");
    assertEquals("java.util.List", resolved.toString()); // Works on both versions
}
```