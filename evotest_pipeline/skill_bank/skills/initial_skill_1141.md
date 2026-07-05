---
name: template-parameter-type-validation
description: When decoding or parsing messages that contain mixed-type template parameters (e.g., both String and CtTypeReference), test that all parameter types are properly handled. This skill helps catch bugs where adding elements of one type incorrectly shadows or replaces elements of another type.
code_tags: ['NULL_CHECK', 'STRING_MANIPULATION']
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-validation

## Instructions

# Template Parameter Type Validation

## Instructions

- WHEN the TG encounters a method that validates, processes, or stores template/protocol parameters (e.g., `Tk103ProtocolDecoder`, or any decoder/parser that extracts typed parameters from messages)
- THEN the TG should write a test that provides **both a `String` type parameter AND a non-String type parameter** (e.g., `CtTypeReference`, `Integer`, `Boolean`) in the same invocation, and verify that:
  1. All parameters are stored/processed correctly without one overwriting another
  2. No `NullPointerException` or `ClassCastException` is thrown during the processing
  3. If a collection or map is used to store parameters, both types of entries are present and distinct after processing
- Common pitfalls to avoid:
  - Testing only with `String` type parameters — this misses bugs where non-String types cause shadowing/overwriting
  - Assuming that order of addition doesn't matter — test both (String first, non-String first)
  - Forgetting to verify that the number of stored parameters equals the number of inputs (no silent omissions)
- Concrete example (correct):
  ```java
  // When decoder has a method like: processParameters(List<Object> params)
  // Test with mixed types:
  List<Object> params = new ArrayList<>();
  params.add("someString");
  params.add(new CtTypeReference<>(Integer.class));  // non-String type
  decoder.processParameters(params);
  // Verify both are present:
  assertEquals(2, decoder.getParameterCount());
  assertEquals("someString", decoder.getParameter(0));
  assertNotNull(decoder.getParameter(1)); // non-String not lost
  ```
- Concrete example (incorrect — misses the bug):
  ```java
  // Only tests String parameters — this would NOT catch the bug:
  List<Object> params = new ArrayList<>();
  params.add("param1");
  params.add("param2");
  decoder.processParameters(params);
  // This passes even if non-String types are silently dropped
  ```
- The test should expect **successful execution** (no exceptions) on the fixed version, and may throw `NullPointerException`, `ArrayIndexOutOfBoundsException`, or produce incorrect counts on the buggy version.