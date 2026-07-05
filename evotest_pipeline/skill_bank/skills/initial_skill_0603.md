---
name: template-parameter-type-validation
description: When validating proxy template parameters or any API that accepts both type-safe references and plain strings, test that the validation/logic works correctly for all supported parameter types — not just the most common one. The TG should include at least one test case using each possible parameter type variant.
code_tags: ['VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters an API method that accepts template/proxy parameters that can be of multiple types (e.g., both `CtTypeReference` and `String` types), and the method is expected to process or validate them uniformly:
  - THEN the TG should write **parametric tests** that cover **all supported parameter types**, not just the most obvious or commonly used one.
  - Specifically, include at least one test case where the parameter is a **plain String** (e.g., `"java.lang.Runnable"`) and at least one where the parameter is a **type-safe reference** (e.g., a `CtTypeReference` wrapping `Runnable.class`).
  - The test should verify that the method produces the **same outcome** (e.g., validation success, correct return value, same behavior) for all parameter type variants.
  - If the method is supposed to validate parameters (e.g., checking that a class exists or is loadable), verify that **invalid parameters of each type** are handled uniformly (e.g., both a bad String and a bad CtTypeReference should throw the same exception).
  - **Common pitfall**: Testing only one parameter type (e.g., only `CtTypeReference` or only `String`), missing the bug where the other type bypasses validation or is handled differently.

- WHEN the triggering test or bug report involves an API that accepts **different representations** of the same conceptual parameter (e.g., class literal vs class name string vs type reference):
  - THEN the TG should explicitly enumerate all supported parameter representations and test each one in isolation.
  - Verify that the buggy behavior (e.g., missing validation, incorrect processing) manifests for **at least one representation but not others**, indicating a type-specific code path.

### Example (Correct Test Pattern)

```java
// Correct: tests ALL supported parameter types
@Test
void testValidationWithStringType() {
    SpoonAPI launcher = new Launcher();
    // Using String type - should also validate and call the same logic
    boolean result = launcher.processTemplateParameter("java.lang.Runnable");
    assertTrue(result);
}

@Test
void testValidationWithCtTypeReference() {
    SpoonAPI launcher = new Launcher();
    // Using CtTypeReference - does not trigger the same validation in buggy version
    boolean result = launcher.processTemplateParameter(
        launcher.getFactory().Type().createReference(Runnable.class)
    );
    assertTrue(result); // FAILS on buggy version - validation skipped
}
```

### Example (Incorrect Test Pattern)

```java
// Incorrect: only tests CtTypeReference, misses the String bug
@Test
void testValidation() {
    SpoonAPI launcher = new Launcher();
    CtTypeReference<?> ref = launcher.getFactory().Type().createReference(Runnable.class);
    boolean result = launcher.processTemplateParameter(ref);
    assertTrue(result);
    // String type is never tested - the bug that affects String parameters is missed
}
```

### Concrete Values to Use

- For the Spoon Launcher API, the two parameter types to test are:
  - `CtTypeReference<?>` (e.g., created via `factory.Type().createReference(SomeClass.class)`)
  - `String` (e.g., `"some.fully.qualified.ClassName"`)
- The validation method checks whether the parameter class is loadable/valid; invalid inputs should throw or return an error indicator for both types.