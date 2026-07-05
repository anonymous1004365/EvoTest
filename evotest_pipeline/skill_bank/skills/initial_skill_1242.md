---
name: protocol-parameter-type-validation
description: When decoding protocol frames that use parameterized key-value pairs
  with alternative value types (e.g., String vs CtTypeReference), always test with
  each unique value type to ensure type-specific decoding logic is exercised. This
  skill helps catch bugs where the protocol decoder handles one value type correctly
  but fails on another.
code_tags:
- EXCEPTION_HANDLING
- VALIDATION
- NULL_CHECK
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# protocol-parameter-type-validation

## Instructions

# Protocol Parameter Type Validation

## Instructions

- WHEN the TG encounters a protocol decoder that processes key-value pairs where values can be one of multiple Java types (e.g., a `String` parameter value, a `CtTypeReference` parameter value, or a custom object), and the decoder uses type-based logic (e.g., `instanceof` checks, type casts, or conditional branching on the parameter's Java class), THEN the TG should write parametric tests that pass each distinct value type through the decoder.

- WHEN writing such a test, include test cases for:
  1. **String-type parameters**: e.g., a parameter with a `String` value like `"someValue"`.
  2. **Non-String-type parameters**: e.g., a parameter with a `CtTypeReference` value (or another wrapper/domain type) such as a type reference object.
  3. **Mixed parameters**: where some entries are String values and others are non-String values in the same map/collection.

- The test MUST verify that:
  - The decoder correctly processes the value according to its type (e.g., String values printed as-is, CtTypeReference values converted via `toString()` or other type-specific handling).
  - No `ClassCastException`, `NullPointerException`, or silent incorrect output occurs for any value type.
  - The output (e.g., decoded message string) matches the expected format for each input type.

- **Common pitfalls to avoid (the TG might do wrong without this skill)**:
  - ❌ Testing only with `String` parameter values, assuming all parameters are Strings.
  - ❌ Not testing the "alternative" decoding path at all (e.g., only testing the primary/normal path).
  - ❌ Assuming a `toString()` or `String.valueOf()` works uniformly across all value types when the code uses `instanceof`-based dispatch.
  - ❌ Forgetting that when a value is not a String, the code might try to cast it to a specific type — this cast must be tested.

- **Correct example** (parametric test covering multiple value types):
  ```java
  @ParameterizedTest
  @MethodSource("provideParameters")
  void testDecodeWithParameterTypes(Map<String, Object> parameters, String expectedOutput) {
      FlextrackProtocolDecoder decoder = new FlextrackProtocolDecoder(null);
      // Build a message/request containing the given parameters
      // ...
      String result = decoder.decode(channel, remoteAddress, msg);
      assertEquals(expectedOutput, result);
  }
  
  static Stream<Arguments> provideParameters() {
      return Stream.of(
          // String-type parameter
          Arguments.of(Map.of("param1", "hello"), "expected_string_output"),
          // CtTypeReference-type parameter (or other non-String type)
          Arguments.of(Map.of("param1", new CtTypeReference(String.class)), "expected_reference_output"),
          // Mixed parameters
          Arguments.of(Map.of("param1", "hello", "param2", new CtTypeReference(Integer.class)), "expected_mixed_output")
      );
  }
  ```

- **Incorrect example** (only tests String values):
  ```java
  @Test
  void testDecodeWithStringParameters() {
      Map<String, Object> parameters = Map.of("param1", "hello");
      FlextrackProtocolDecoder decoder = new FlextrackProtocolDecoder(null);
      String result = decoder.decode(channel, remoteAddress, msg);
      assertEquals("expected_string_output", result);
      // BUG: Does not test with CtTypeReference or other non-String types
      // The buggy code handles String correctly but fails on CtTypeReference
  }
  ```