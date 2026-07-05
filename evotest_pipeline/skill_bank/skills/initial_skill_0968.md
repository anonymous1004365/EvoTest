---
name: template-parameter-type-validation
description: When parsing protocol parameters from a generic/typed list (e.g., Map<String, Object>), test that each parameter type is validated individually rather than assuming all values share the same type as the first encountered. Use this skill for protocol decoders that build parameter maps with mixed-type values.
code_tags: ['VALIDATION', 'TYPE_CONVERSION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a protocol decoder that parses named parameters from a `Map<String, Object>` or similar generic map, where parameter templates define expected parameter names and values are parsed from a string
- THEN the TG should test that **each parameter value is individually type-checked or converted**, not that all values share the same type as the first item in a list/pair. Specifically:
  - When a parameter template specifies a type (e.g., `CtTypeReference` for a class/interface type), the decoder must handle that type correctly for **each** parameter independently
  - Test with at least **two parameters of different types** (e.g., one `String`, one `CtTypeReference`) where both appear in the same input string
  - The test should assert that both parameters are decoded with their respective types, not that the second parameter's value erroneously assumes the type of the first
  - Verify that a `ClassCastException` is **not** thrown when processing the second parameter
- Common pitfalls to avoid:
  - Testing only with a single parameter — this masks the bug
  - Testing only with parameters of the same type (e.g., both `String`) — this masks the bug
  - Assuming that `Object`-typed map values are safely polymorphic — they are NOT when the decoder naively casts based on the first parameter's template type
- Correct example (catches the bug):
  ```java
  Map<String, Object> params = decoder.decode("io,1.0,param1=hello,param2=java.lang.String");
  assertEquals("hello", params.get("param1"));
  assertEquals(CtTypeReference.class, params.get("param2").getClass());
  ```
- Incorrect example (misses the bug):
  ```java
  Map<String, Object> params = decoder.decode("io,1.0,param1=hello");
  // Only one parameter — never triggers the type confusion
  ```