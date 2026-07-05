---
name: template-parameter-type-validation
description: When validating parameters of a template/proxy configuration, test with multiple distinct types including String and the expected domain type to ensure the validation handles all template parameter types correctly.
code_tags: ['ABSOLUTE_PATH_FILE_MOVE', 'VALIDATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters validation logic for template/proxy parameters that stores or processes parameters from a configuration object
- THEN it should write parametric tests that pass different types of parameter values, including at minimum:
  1. A `String` value parameter
  2. A domain-specific type value parameter (e.g., `CtTypeReference<?>` for Spoon templates)
- The test should verify that:
  - Each parameter type is validated and stored correctly
  - The validation does NOT throw unexpected exceptions for valid parameter types
  - The stored/inspected parameters match the expected values after processing
- Common pitfalls to avoid:
  - Only testing with `String` type parameters, missing the case where domain-specific types (like `CtTypeReference`) are used as parameter values
  - Assuming all template parameters are strings without checking the actual parameter type expectations from the template processor
  - Not iterating through or inspecting all stored parameters after validation, missing incorrect internal state
- Example correct test pattern:
```java
@Test
public void testValidateParameters() {
    TemplateConfig config = new TemplateConfig();
    config.addParameter("type", someTypeReference);  // domain type
    config.addParameter("name", "testValue");         // String type
    // validate and verify both are stored correctly
}
```
- Example WRONG test pattern (missing domain type):
```java
@Test
public void testValidateParameters() {
    TemplateConfig config = new TemplateConfig();
    config.addParameter("name", "testValue");  // only tests String
    // misses validation failure with non-String types
}
```