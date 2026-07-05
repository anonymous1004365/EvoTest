---
name: template-parameter-type-validation
description: When parsing or validating template parameters that can have multiple types (String, class references, etc.), the test generator should test with all supported types especially non-String types like CtTypeReference to catch cases where type-sensitive comparisons fail.
code_tags: ['NULL_CHECK', 'VALIDATION', 'BOUNDARY_CHECK', 'TYPE_CONVERSION', 'STATE_MUTATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that processes template/proxy parameters by iterating over parsed tokens and checking their types (e.g., checking if a parameter value is a String vs. a CtTypeReference or other class type)
- THEN the TG should write a test that:
  1. Creates template parameters of **all supported types** that the code claims to handle — particularly non-String types like `CtTypeReference`, `Class<?>`, etc.
  2. Verifies that the validation logic correctly recognizes each type and does NOT throw a `ClassCastException` or silently skip processing non-String types
  3. For each type, verify that the parameter is correctly processed (e.g., added to a collection, validated against constraints) rather than only testing with String parameters
- Common pitfalls to avoid:
  - Testing only with String-type parameters when the code also handles `CtTypeReference` or `Class` type parameters
  - Testing only the "happy path" of valid parameters without testing that different types are all correctly processed
  - Assuming that because a parameter passes initial parsing, it will be correctly handled during validation/processing (type-specific comparisons may fail later)
- Concrete example of correct testing (from the actual bug):
  ```java
  // BUGGY: only tested with String parameters, missing CtTypeReference case
  ProxyParam param = new ProxyParam("someString", "value");
  processor.addParam(param);
  
  // FIXED: also test with CtTypeReference parameter
  CtTypeReference<?> ref = ...;
  ProxyParam param2 = new ProxyParam("someRef", ref);
  processor.addParam(param2);
  ```
- Concrete example of incorrect testing:
  ```java
  // BUGGY: Only tests String parameters
  ProxyParam param = new ProxyParam("name", "value");
  // Missing: ProxyParam param2 = new ProxyParam("typeRef", someTypeReference);
  ```