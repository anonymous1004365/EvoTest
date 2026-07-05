---
name: package-request-target-url-creation-validation
description: When constructing URL coding strategy targets, test that the strategy
  correctly validates path patterns and handles requests to non-existent or invalid
  targets. Use this skill when a method creates or resolves URL-encoded paths with
  parameter templates.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- ARGUMENT_VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# package-request-target-url-creation-validation

## Instructions

# Package Request Target URL Creation Validation

## Instructions

WHEN the TG encounters a method that constructs or resolves a URL coding strategy target (e.g., `PackageRequestTargetUrlCodingStrategy` or similar classes that handle URL-to-component mapping with path parameters):

- THEN the TG should write parametric tests that verify the strategy correctly handles **invalid or non-existent targets** (e.g., passing a class or package path that does not exist in the codebase).

- Include test cases where:
  1. The path template contains a parameter segment (e.g., `"${param}"`) that must be resolved to a real class or component.
  2. The parameter value in the request URL points to a **non-existent class** or an **invalid package path**.
  3. The request maps to a component that exists but the path structure is malformed (e.g., missing required segments).

- The test should verify that an appropriate exception is thrown (e.g., `ClassNotFoundException`, `IllegalArgumentException`, or a custom wrapping exception) when the target cannot be resolved.

- **Common pitfalls:**
  - Testing only paths that resolve successfully (happy path) and never testing resolution failures.
  - Assuming that all template parameters (e.g., `${param}`) will resolve to valid classes — always test with invalid/random parameter values.
  - Forgetting that `String.replace()` or simple concatenation may produce paths that look valid but point to non-existent targets.
  - Not checking the **state** of the strategy object after a failed resolution (it should remain in a consistent state for future requests).

### Example Test Pattern (Correct)

```java
// CORRECT: Tests both existing and non-existing targets
@Test
void testEncodeDecodeWithNonExistentTarget() {
    // Setup
    PackageRequestTargetUrlCodingStrategy strategy = new PackageRequestTargetUrlCodingStrategy(
        "somePrefix", SomeExistingClass.class, "${classParam}");

    // Test with existing target
    CharSequence encoded = strategy.encode(new PackageRequestTarget(SomeExistingClass.class));
    Assertions.assertNotNull(encoded);

    // Test with non-existent target — should throw
    String requestUrl = "somePrefix/non.existent.ClassName";
    Assertions.assertThrows(SomeException.class, () -> {
        strategy.decode(requestUrl);  // or strategy.resolveTarget(requestUrl)
    });
}
```

### Example Pitfall (Incorrect)

```java
// WRONG: Only tests happy path, never validates failure cases
@Test
void testEncodeDecode() {
    PackageRequestTargetUrlCodingStrategy strategy = new PackageRequestTargetUrlCodingStrategy(
        "somePrefix", SomeExistingClass.class, "${classParam}");

    CharSequence encoded = strategy.encode(new PackageRequestTarget(SomeExistingClass.class));
    // Only tests existing class — misses bug where non-existent class causes state corruption
    Assertions.assertNotNull(encoded);
}
```

- **When writing parametric tests**, vary the path parameter values to include:
  - Valid, existing class names
  - Invalid class names (e.g., `"does.not.Exist"`)
  - Empty path segments (e.g., `"somePrefix/"` with empty remainder)
  - Paths that resolve to classes not compatible with the expected component type

- **Verify state consistency**: After a failed resolution attempt, ensure the strategy object can still successfully resolve a valid target on a subsequent call. This catches bugs where failed attempts corrupt internal state (e.g., caching wrong values).