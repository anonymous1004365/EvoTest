---
name: snippet-template-parameter-validation
description: When creating snippet tests that involve template parameter resolution
  (e.g., CtTypeReference, types, and parameters), ensure the test covers both String
  and non-String parameter types, including CtTypeReference<?> objects accessed via
  reflection. Apply this skill when testing code that collects snippet templates with
  parameter metadata.
code_tags:
- VALIDATION
- BOUNDARY_CHECK
- TYPE_CONVERSION
- STATE_MUTATION
- ORDER_DEPENDENCY
test_pattern: PARAMETRIC_TEST
---

# snippet-template-parameter-validation

## Instructions

# Snippet Template Parameter Validation

## Instructions

- WHEN the TG encounters code that collects or validates snippet template parameters (e.g., from `CtAnnotation`, `CtType`, `CtMethod`, or `CtExecutableReference`),
  - AND the parameters may be of mixed types (e.g., both `String` and `CtTypeReference<?>` values),
- THEN the TG should create a parametric test that explicitly passes parameters of different types (e.g., a `String` value plus a `CtTypeReference<?>` value obtained via `factory.Type().get(SomeClass.class)`),
  - AND verify that the method correctly handles non-String parameter types without skipping or failing,
  - AND confirm that the final generated code/snippet includes all parameters correctly (i.e., no parameters are lost or silently dropped).

- Avoid these common mistakes:
  - **Mistake 1**: Testing only with `String` type parameters. This masks bugs where non-String types (e.g., `CtTypeReference`, `Integer`, `CtAnnotation`) are silently skipped or corrupted during template parameter collection.
  - **Mistake 2**: Assuming that the parameter list is only populated from one source (e.g., only annotation string values) without verifying that other sources (e.g., type references from related interfaces, superclasses, or other methods) are also included.
  - **Mistake 3**: Neglecting to assert on the **number or order** of collected parameters — the test must fail on the buggy version due to missing or misordered parameters, not just superficially pass.

- Correct example (what the test should do):
  ```java
  // Build a snippet template with parameters of different types:
  // - param1: a String value "someString"
  // - param2: a CtTypeReference<?> obtained from a specific class
  snippetBuilder.addParameter("param1", "someString");
  snippetBuilder.addParameter("param2", factory.Type().get(SomeClass.class));
  String result = snippetBuilder.build();
  // Assert that the result contains both parameters:
  assertTrue(result.contains("someString"));
  assertTrue(result.contains("SomeClass"));
  ```

- Incorrect example (what the test should avoid):
  ```java
  // Only testing String parameters:
  snippetBuilder.addParameter("param1", "someString");
  snippetBuilder.addParameter("param2", "anotherString");
  String result = snippetBuilder.build();
  // This passes in both buggy and fixed versions, masking any issue with non-String types.
  ```