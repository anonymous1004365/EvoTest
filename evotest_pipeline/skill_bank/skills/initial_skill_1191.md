---
name: template-parameter-type-coercion
description: When decoding protocol messages with template-generated parsers, test
  that the decoder correctly handles type mismatches between template parameter types
  and actual cell types, especially when String and non-String types are mixed.
code_tags:
- VALIDATION
- NULL_CHECK
- BOUNDARY_CHECK
- BOX_PROTOCOL_DECODING
- ALTERNATIVE_PROTOCOL_DECODING
test_pattern: PARAMETRIC_TEST
---

# template-parameter-type-coercion

## Instructions

# Template Parameter Type Coercion in Protocol Decoders

## Instructions

- WHEN the TG encounters a protocol decoder that uses a template-based or generic parameter map (e.g., storing values as `String` but the parameter or field expects a `CtTypeReference` or non-String type)
- THEN the TG should write a test that:
  1. Supplies a message with a field/parameter where the template value is one type (e.g., a `String` representation of a class name like `"java.lang.String"`) but the corresponding property expects a different concrete type (e.g., `CtTypeReference`).
  2. Verifies that the decoder either:
     - Correctly coerces the template `String` into the expected type (e.g., by constructing a `CtTypeReference` from the `String` class name), OR
     - Throws a meaningful exception (like `IllegalArgumentException`, `ClassNotFoundException`, or a protocol-specific decode exception) when coercion is not possible.
  3. Checks that no silent mis-decoding occurs (e.g., the decoder does not silently ignore the type mismatch and use a default/incorrect value like `null` or an empty string).
  4. Includes edge cases such as: empty string value, `null` value, a value that is a `String` that cannot be parsed into the target type, and a valid `String` that correctly maps to the target type (the "happy path").

- Common pitfalls to avoid:
  - Testing only with `String`-to-`String` mappings and assuming all template parameters are strings.
  - Failing to test with a value whose type mismatches the expected parameter type (e.g., a `String` where the parameter expects a `CtTypeReference`, `Integer`, or `Boolean`).
  - Only testing the "happy path" where all values are strings and all fields accept strings.
  - Assuming the decoder will throw an exception; it might silently convert/ignore the mismatch, leading to a bug that only manifests later.

- Example of a correct test approach:
  ```java
  // Test that a template parameter expecting CtTypeReference
  // is correctly parsed from a String class name
  @Test
  void testTemplateParameterTypeCoercion() {
      Map<String, Object> templateParams = new HashMap<>();
      templateParams.put("type", "java.lang.String");  // String value
      // expected: decoder converts to CtTypeReference.forClass(String.class)
      // assert that the decoded object has the correct type reference
  }
  ```

- Example of an incorrect test approach:
  ```java
  // WRONG: Only tests with String-type template parameters
  @Test
  void testDecodeWrong() {
      Map<String, Object> templateParams = new HashMap<>();
      templateParams.put("type", "someStringValue");
      // Expected: decoder uses it as-is (String), but the field
      // actually needs a CtTypeReference — silent bug!
  }
  ```