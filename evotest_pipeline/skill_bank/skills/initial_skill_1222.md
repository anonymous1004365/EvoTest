---
name: proxy-template-param-type-validation
description: When validating proxy template parameters (parsing variable names from
  template strings), the test generator should test with both String and non-String
  type inputs (e.g., CtTypeReference) to ensure type-safe comparison logic handles
  all parameter types correctly.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- ALTERNATIVE_PROTOCOL_DECODING
- ARGUMENT_VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# proxy-template-param-type-validation

## Instructions

# Proxy Template Parameter Type Validation

## Instructions

- WHEN the TG encounters code that parses variable names from template strings (e.g., `{param_name}` or `$param_name`) and compares/extracts them against a collection of expected parameter objects
- THEN the TG should write a parametric test that supplies both `String` type parameters and non-String type parameters (e.g., `CtTypeReference<String>`, `Integer`, custom domain objects) as the expected parameter collection
- The test must verify that:
  1. Template variable names matching String parameters are correctly resolved
  2. Template variable names matching non-String parameters (e.g., `CtTypeReference<String>`) do NOT cause a `ClassCastException`, `IllegalArgumentException`, or silent incorrect match
  3. The method correctly converts/normalizes parameter types before comparison (e.g., via `toString()`, `getSimpleName()`, or type-erased name extraction)
- Common pitfalls to avoid:
  - Testing only with `String` type parameters in the collection — this hides bugs where the code assumes all parameters are Strings and performs unchecked casts
  - Testing only one non-String type — use at least two distinct non-String types (e.g., `CtTypeReference<String>`, `Integer`, or a real proxy/interface type from the codebase)
  - Verifying only the happy path — include a case where the template variable does NOT match any parameter, to ensure no false positive match
- Example of a correct test pattern:
  ```java
  // Given a template with variable {name} and parameters of mixed types
  parameters.add("name");  // String type
  parameters.add(someCtTypeReference);  // non-String type with toString() = "name"
  
  // When resolving the variable
  Object resolved = resolver.resolve("{name}", parameters);
  
  // Then the String parameter should match (not the non-String one)
  assertThat(resolved).isEqualTo("name");
  ```
- Example of an incorrect test pattern (what the TG might write without this skill):
  ```java
  // BAD: only tests String parameters
  parameters.add("name");
  parameters.add("age");
  
  // This would pass even with the bug, missing the ClassCastException scenario
  ```