---
name: validation-of-dependency-scope-against-valid-list
description: When writing tests for model validation logic that checks dependency
  scope values, test with invalid scope values to ensure the validator correctly reports
  errors. This is particularly important when the validation logic uses a Set or List
  of allowed values and reports violations for any value not in the allowed set.
code_tags:
- VALIDATION
- STATE_MUTATION
test_pattern: PARAMETRIC_TEST
---

# validation-of-dependency-scope-against-valid-list

## Instructions

# Validation of Dependency Scope Against Allowed Values

## Instructions

- WHEN the TG encounters validation logic that checks a field (e.g., dependency scope) against a fixed set of allowed values (e.g., a Set<String> of valid scopes like "compile", "provided", "runtime", "test", "system", "import")
- THEN the TG should write a test that provides an input with an invalid/unknown value for that field and verifies that:
  1. The validator reports a validation error (not a warning)
  2. The error message contains the invalid value and/or indicates the scope is invalid
  3. The build/validation fails with the expected number of violations

- Include test cases that cover:
  - **Invalid scope value**: e.g., a dependency with scope="something_else" that is not in the allowed set
  - **Case sensitivity**: e.g., scope="Test" (capitalized) to ensure the check is case-sensitive
  - **Null/empty scope**: if the validation also allows defaulting, test null/empty separately from invalid values
  - **Edge cases near the boundary**: e.g., values that look similar to valid scopes like "complie" (typo)

- Common pitfalls to avoid:
  - Testing only valid scope values; the bug is precisely about invalid values not being caught
  - Using a scope value that might be silently defaulted/fixed by other logic (e.g., "default" or empty string)
  - Forgetting to check the error count or error message content — verify the violation is actually reported
  - Assuming the validation is case-insensitive unless the code explicitly normalizes case

### Example (correct approach)

```java
// POM input with invalid scope
// <dependency>
//   <groupId>test</groupId>
//   <artifactId>a</artifactId>
//   <version>1.0</version>
//   <scope>something_else</scope>
// </dependency>

@Test
void testInvalidDependencyScope() {
    SimpleProblemCollector result = validate("bad-dependency-scope.xml");
    assertEquals(1, result.getErrors().size(), "Should report 1 error for invalid scope");
    assertTrue(result.getErrors().get(0).contains("something_else"),
        "Error message should contain the invalid scope value");
}
```

### Example (incorrect approach)

```java
// WRONG: Only testing valid scopes, missing the bug
@Test
void testDependencyScope() {
    SimpleProblemCollector result = validate("good-dependency.xml");
    assertEquals(0, result.getErrors().size());
    // This would NOT catch the bug where invalid scopes pass through
}
```