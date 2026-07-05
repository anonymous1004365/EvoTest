---
name: dependency-version-illegal-character-validation
description: Validates dependency version strings contain only legal characters (no
  path separators like '/', '\', ':' etc.). Apply when testing dependency version
  validation in model validators.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# dependency-version-illegal-character-validation

## Instructions

# Dependency Version Illegal Character Validation

## Instructions

- WHEN the TG encounters code that validates dependency version strings (e.g., `DefaultModelValidator.validateStringNotEmpty` for `"dependencies.dependency.version"`)
- THEN it should test that version strings containing illegal filesystem characters such as `/`, `\`, `:`, `"`, `<`, `>`, `|`, `?`, `*` are detected as errors
  - For example, a version like `"1/1"` should produce a validation error because `/` is in `ILLEGAL_VERSION_CHARS`
  - The test should use test resource POM files with `bad-dependency-version.xml` or similar, containing dependencies with illegal characters in the version
  - Verify using `SimpleProblemCollector` that errors contain `"dependencies.dependency.version"` for the offending dependency
  - Expect at least as many errors as there are illegally-versioned dependencies

- WHEN validating dependency versions, also test that unresolved property expressions like `${missing.property}` trigger validation errors about version format/characters (since `${` and `}` could contain illegal chars after interpolation)
  - The existing test `testBadDependencyVersion()` expects 2 errors from a POM with 3 dependencies: one valid (`0.2`), one with unresolved property (`${missing.property}`), and one with illegal char (`1/1`)

- Common pitfall: Testing only for empty/missing dependency versions without testing for illegal characters in the version string. Another pitfall: expecting a single error when there are multiple bad dependencies — the count must match exactly the number of offending dependencies.

**Correct example:**
```java
public void testBadDependencyVersion() throws Exception {
    SimpleProblemCollector result = validateRaw("bad-dependency-version.xml",
        ModelBuildingRequest.VALIDATION_LEVEL_STRICT);
    assertViolations(result, 0, 2, 0); // 2 errors: unresolved property + illegal char
    assertTrue(result.getErrors().get(0).contains("dependencies.dependency.version"));
    assertTrue(result.getErrors().get(1).contains("dependencies.dependency.version"));
}
```

**Incorrect example (too few errors expected):**
```java
public void testBadDependencyVersion() throws Exception {
    SimpleProblemCollector result = validateRaw("bad-dependency-version.xml",
        ModelBuildingRequest.VALIDATION_LEVEL_STRICT);
    assertViolations(result, 0, 1, 0); // WRONG: only counts one bad version
}
```