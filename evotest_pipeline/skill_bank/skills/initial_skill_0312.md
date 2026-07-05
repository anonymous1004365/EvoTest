---
name: jsop-template-parameter-validation
description: When validating parameters for proxy/template nodes from JSON/Jsop strings,
  test with all supported types found in the implementation, not just the most common
  one. The TG should expand coverage beyond String types to include CtTypeReference
  and other parameter types.
code_tags:
- NULL_CHECK
- BOUNDARY_CHECK
- VARIABLE_SCOPE
- STRING_PARSING
test_pattern: PARAMETRIC_TEST
---

# jsop-template-parameter-validation

## Instructions

# Jsop Template Parameter Type Validation

## Instructions

WHEN the TG encounters a method that processes or validates parameters extracted from Jsop/JSON strings for creating proxy or template nodes (look for patterns like `JsonJsopTokenizer`, `getValue`, template parameter parsing):

- THEN the TG should identify **ALL** parameter types that the implementation supports by examining the `getValue()` method or parameter conversion logic — especially check for `CtTypeReference` (CtType) support in addition to `String` and primitive types.

- THEN the TG should write **parametrized tests** that exercise the template parameter validation with each supported type, including:
  - `String` parameters
  - `CtTypeReference<String>` (or similar `CtType` wrapped types)
  - Other supported types such as booleans, numbers, etc.

- The test should verify that when a specific parameter value is provided (e.g., `"{String}myStringProp"` vs `"{=String}myStringProp"`), the parsing correctly identifies the type and sets the value accordingly. On the buggy version, tests should expect a **`NullPointerException`** or incorrect parsing behavior when certain types are used.

- Common pitfalls to avoid:
  - **Testing only String parameters**: The most common mistake is only testing `{String}name` format, missing `{=CtType}name` or other type-prefixed parameter formats
  - **Assuming all parameters are plain strings**: Template parameters can carry type information that affects parsing behavior
  - **Not checking the Jsop tokenizer behavior**: The `JsonJsopTokenizer` may handle special escape sequences (e.g., `\q`, `\s`, `\n`) that affect parameter value extraction
  - **Forgetting to test boundary cases**: Empty values, special characters in values, and nested quote escaping

### Correct test approach example:
```java
// Test with String parameter
@Test
public void testAddNodeTemplateWithStringParam() {
    // Template with {String}param
}

// Test with CtTypeReference parameter
@Test
public void testAddNodeTemplateWithCtTypeParam() {
    // Template with {=String}param or {=CtType}param
}

// Parametrized test for all types
@ParameterizedTest
@ValueSource(strings = {"{String}prop", "{=String}prop"})
public void testParameterTypes(String paramDef) {
    // Verify parsing doesn't throw NPE and correctly handles the type prefix
}
```

### Incorrect approach to avoid:
```java
// BAD: Only tests String type, misses CtTypeReference bugs
@Test
public void testAddNodeWithExpandedName() {
    // Only uses {String}name format - will miss the bug!
}
```