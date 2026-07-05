---
name: method-name-convention-validation
description: When a code quality rule validates naming conventions (e.g. method names
  must match a regex pattern), test that the rule correctly handles edge cases like
  empty names, null names, names with numbers, and names matching the pattern exactly.
  Use this skill when testing checks/rules that enforce naming conventions or regex-based
  validations.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# method-name-convention-validation

## Instructions

# Method Name Convention Validation

## Instructions

- WHEN the TG encounters a rule/check class that validates naming conventions (such as method names, class names, or variable names) against a regex pattern,
- THEN the TG should create a parameterized test that verifies both valid and invalid names, including:
  - Names that match the expected convention (should pass without violations)
  - Names that violate the convention (should produce violations)
  - **Edge cases**: empty string `""`, null value, names with numbers, names with special characters, names with only lowercase/uppercase letters
- The TG should also verify that the check correctly handles cases where the name is null (avoiding NullPointerException) by ensuring the check gracefully reports a violation or skips without crashing.
- **Common pitfalls**: 
  - Testing only one valid and one invalid name — this misses edge cases like empty names, numeric prefixes, or very short names
  - Not testing null input — the check may use `.matches()` on the name directly without a null guard, causing a NullPointerException during analysis
  - Assuming the pattern is case-sensitive without testing both lowercase and uppercase variants
  - Not testing names that partially match the pattern (e.g., a name that starts correctly but has extra invalid characters at the end)

### Correct Example

```java
@ParameterizedTest
@ValueSource(strings = {"", " ", "123", "null", "a"})
void shouldReportViolationForInvalidNames(String invalidName) {
    MethodNameCheck check = new MethodNameCheck();
    check.setFormat("^[A-Z][a-zA-Z0-9]*$");
    
    MethodTree methodTree = createMethodTree(invalidName);
    check.visitNode(methodTree);
    
    assertThat(check.getViolations()).isNotEmpty();
}

@ParameterizedTest
@ValueSource(strings = {"ValidName", "Name1", "X", "Abc"})
void shouldNotReportViolationForValidNames(String validName) {
    MethodNameCheck check = new MethodNameCheck();
    check.setFormat("^[A-Z][a-zA-Z0-9]*$");
    
    MethodTree methodTree = createMethodTree(validName);
    check.visitNode(methodTree);
    
    assertThat(check.getViolations()).isEmpty();
}

@Test
void shouldHandleNullNameWithoutCrashing() {
    MethodNameCheck check = new MethodNameCheck();
    check.setFormat("^[A-Z][a-zA-Z0-9]*$");
    
    MethodTree methodTree = createMethodTree(null);
    // Should not throw NullPointerException
    assertDoesNotThrow(() -> check.visitNode(methodTree));
}
```

### Incorrect Example

```java
// ❌ BAD: Only tests one invalid and one valid case — misses edge cases
@Test
void testNamingConvention() {
    MethodNameCheck check = new MethodNameCheck();
    check.setFormat("^[A-Z][a-zA-Z0-9]*$");
    
    // Only tests this one case
    assertThat(check.visitNode(createMethodTree("bad_name"))).isTrue();
    assertThat(check.visitNode(createMethodTree("GoodName"))).isFalse();
}
```