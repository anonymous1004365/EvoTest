---
name: template-proxy-parameter-type-validation
description: When validating proxy template parameters, test with ALL supported parameter
  types (both String and non-String like CtTypeReference). The client may pass object
  references that bypass string-only validation logic, leading to uncaught type mismatches.
code_tags:
- STATE_MUTATION
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# template-proxy-parameter-type-validation

## Instructions

# Template Proxy Parameter Type Validation

## Instructions

- WHEN the TG encounters code that validates proxy template parameters (e.g., checking whether a parameter name exists in a collection of valid parameter names)
- THEN the TG should write tests that provide parameters of DIFFERENT TYPES — specifically both `String` parameters AND non-String typed parameters (such as `CtTypeReference<?>` objects) — to verify the validation logic handles all types correctly
- The TG should verify that when a parameter name is provided as a non-String type (e.g., a `CtTypeReference`), the validation still correctly identifies it as a valid or invalid parameter
- WHEN validating parameter names, the TG should test with:
  - `String` type parameters (e.g., `"param1"`, `"param2"`)
  - Non-String type parameters (e.g., `CtTypeReference<?>` objects with the same qualified name)
- The TG should expect that on the BUGGY version, non-String typed parameters with a valid name may NOT be recognized during validation and cause unexpected behavior (e.g., throwing an exception or silently failing)
- The TG should expect that on the FIXED version, all parameter types with matching names are correctly validated

**Common pitfalls:**
- Testing only with `String` type parameters — this misses the bug entirely since the bug is specifically about non-String type handling
- Testing only whether parameters are correctly set without verifying validation rejects invalid ones
- Assuming all parameters are `String` instances — proxy template parameters can be `CtTypeReference` objects or other types

**Example (correct):**
```java
// Test with both String and CtTypeReference parameters
String param1 = "param1";
CtTypeReference<?> param2 = new CtTypeReference<>("param2");

// Verify both are valid parameters
assertDoesNotThrow(() -> validate(param1));
assertDoesNotThrow(() -> validate(param2));
```

**Example (incorrect — misses the bug):**
```java
// Only testing with String parameters
String param1 = "param1";
assertDoesNotThrow(() -> validate(param1));
// Bug where CtTypeReference params fail validation is NOT caught!
```