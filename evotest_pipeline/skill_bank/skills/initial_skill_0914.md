---
name: jcr-path-square-bracket-validation
description: When testing JCR path validation methods, the TG should test that paths
  containing unclosed square brackets (e.g. 'foo:bar]baz') are correctly rejected
  as invalid. This skill covers validating JCR paths and names with bracket-related
  syntax errors.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# jcr-path-square-bracket-validation

## Instructions

## Guidance

# JCR Path Square Bracket Validation

## Instructions

WHEN the TG encounters a method that validates or parses JCR paths (e.g., `JcrPathParser.validate(String jcrPath)` or `NamePathMapperImpl.getOakPath(String jcrPath)`):

- THEN the TG should test that paths containing unclosed or mismatched square brackets (`[`, `]`) are correctly identified as invalid.
- Specifically, include test cases for paths where a closing bracket `]` appears without a preceding opening bracket `[` — for example `"foo:bar]baz"`.
- Also test paths with unclosed opening brackets — for example `"foo:bar[baz"`.
- Use JUnit parameterized tests with `@CsvSource` or `@MethodSource` to test multiple invalid path patterns concisely.
- Verify that `JcrPathParser.validate(path)` returns `false` for invalid paths and `true` for valid paths.
- For paths that pass through `NamePathMapperImpl.getOakPath()`, verify that an `InvalidPathException` is thrown for invalid paths and a valid Oak path string is returned for valid paths.

Common pitfalls:
- Testing only with valid paths and not including malformed bracket patterns.
- Testing only with simple invalid patterns (e.g., empty string, null) but forgetting bracket-specific edge cases.
- Using only a single test method for each path instead of a parameterized test across multiple invalid inputs.
- Assuming that a path with a closing bracket but no opening bracket might somehow be valid JCR syntax.

### Example (Correct - using parameterized test)

```java
@ParameterizedTest
@CsvSource({
    "foo:bar]baz",
    "[foo:bar",
    "foo:bar]",
    "a[b]c]d",
    "[a[b]c"
})
void testInvalidJcrPathsWithBrackets(String invalidPath) {
    assertFalse(JcrPathParser.validate(invalidPath));
}
```

### Example (Incorrect - not testing bracket edge cases)

```java
@Test
void testInvalidJcrPaths() {
    // Only tests null/empty, misses bracket-specific cases
    assertFalse(JcrPathParser.validate(""));
    assertFalse(JcrPathParser.validate(null));
    // Missing: paths with unclosed or stray brackets
}
```