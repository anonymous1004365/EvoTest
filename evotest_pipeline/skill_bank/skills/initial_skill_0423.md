---
name: template-parameter-type-validation
description: WHEN testing methods that validate proxy template parameters with different Java types (String, CtTypeReference), THEN write tests that verify both type-specific validation and the general rejected-execution exception path. Avoid testing only String type parameters which may bypass type-specific validation logic.
code_tags: ['ARGUMENT_VALIDATION', 'BOUNDARY_CHECK']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that validates template parameters from a proxy or factory context (e.g., checking proxyMethod's parameters against allowed types like String, int, CtTypeReference)
- THEN the TG should write parametric tests that iterate over multiple parameter types (at least String and CtTypeReference) and verify that the method correctly detects unsupported or rejected parameter types
- Include assertions that the method throws a specific exception (e.g., IllegalArgumentException or similar rejected-execution exception) when the parameter type is of a particular non-allowed category
- Common pitfalls:
  - Testing only with String-type parameters, which may pass validation trivially but miss the rejection logic triggered by other parameter types
  - Forgetting to cover edge types like CtTypeReference (a code-model type from a bytecode engineering library) that trigger a different code path in the validation
  - Not asserting the specific exception message or type that distinguishes a validation rejection from a general failure
- Example (correct): param test where one case passes a CtTypeReference parameter and asserts rejection with the expected exception type and message
- Example (incorrect): single test that only passes a String parameter and asserts success without covering the CtTypeReference rejection path