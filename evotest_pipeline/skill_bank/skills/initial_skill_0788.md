---
name: target-type-null-validation
description: When validating proxy template parameters or resolving imports with target
  types, test that null target types are handled gracefully without NullPointerException.
  This skill applies when a method accepts a nullable target type and delegates to
  resolution logic that may fail on null.
code_tags:
- NULL_CHECK
- VALIDATION
- STATE_MUTATION
test_pattern: EXCEPTION_TEST
---

# target-type-null-validation

## Instructions

# Target Type Null Validation

## Instructions

- WHEN the TG encounters a method that accepts a `targetType` parameter (of type `CtTypeReference` or similar) that can be `null`, AND the method internally calls methods like `getImport()` or similar resolution logic on that target type
- THEN the TG should write a test that explicitly passes `null` as the `targetType` argument and verifies that the method handles it gracefully (e.g., returns `null`, returns an empty collection, or throws a meaningful exception like `IllegalArgumentException` rather than a `NullPointerException`)
- The test should include two cases:
  1. The method called with `null` target type should NOT throw a `NullPointerException`
  2. The test should compare behavior between `null` and a valid `CtTypeReference` target type to ensure the null case is deliberately handled
- Common pitfalls to avoid:
  - Do NOT assume the method will accept null — test for it explicitly
  - Do NOT test only with valid types; the bug is specifically about the null case being missed
  - Do NOT catch and ignore exceptions — use `assertThrows` or let the test fail naturally on the buggy version if the fix is not applied

### Example (Correct)
```java
@Test
public void testTargetTypeNull() {
    // This should not throw NullPointerException
    // If the method returns a result, assert it's reasonable (e.g., empty list)
    assertDoesNotThrow(() -> scanner.computeImports(null));
}
```

### Example (Incorrect — what the TG might write without this skill)
```java
@Test
public void testTargetTypeSomeType() {
    // Only tests with a valid type — misses the null case entirely
    CtTypeReference<?> type = factory.Type().get(String.class);
    Set<Import> imports = scanner.computeImports(type);
    assertNotNull(imports);
}
```