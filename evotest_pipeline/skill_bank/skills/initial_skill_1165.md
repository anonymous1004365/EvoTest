---
name: protocol-message-validation
description: When decoding protocol messages that accept multiple data types (e.g.
  numeric and string identifiers), tests must validate that mixed-type or unexpected
  type inputs do not break decoding and that the correct decoding path is chosen for
  each type.
code_tags:
- VALIDATION
test_pattern: PARAMETRIC_TEST
---

# protocol-message-validation

## Instructions

# Protocol Message Validation

## Instructions

- WHEN the TG encounters a protocol decoder that accepts parameters of multiple types (e.g., both `String` and numeric types like `int`/`long` for a device identifier or template parameter),
- THEN the TG should write a parametric test that verifies the decoder correctly handles each supported type without throwing unexpected exceptions or returning incorrect results on the buggy version.
- Specifically, the test must exercise each type variant at least once (e.g., passing a numeric ID, then passing a string ID).
- Verify that for each input type, the decoded output matches the expected protocol response object on the fixed version, while the buggy version may produce a wrong result or throw an exception (e.g., `NullPointerException`, `ClassCastException`, or silently returning a default/empty value).
- Common pitfalls to avoid:
  - Testing only the "happy path" with a single type (e.g., only `String` parameters) and missing the alternative type case.
  - Assuming that a protocol decoder only accepts one kind of value and not checking the actual method signatures/overloads.
  - Not comparing the decoded output between buggy and fixed versions — the bug may manifest as a silently wrong result rather than an exception.
  - Writing a test that passes for both buggy and fixed versions, failing to detect the regression.

### Example (Correct)
```java
// Parametric test that exercises both String and numeric types for a device ID parameter
@ParameterizedTest
@CsvSource({
    "12345, numeric",
    "'ABC123', string"
})
void testDecodeWithMixedTypes(String rawValue, String typeLabel) {
    // Build a message frame using rawValue as the identifier
    // Decode using the protocol decoder
    // On the fixed version, both variants should produce a valid result
    // On the buggy version, one variant may fail or produce wrong output
    assertDoesNotThrow(() -> decoder.decode(channel, remoteAddress, msg));
    Object result = decoder.decode(channel, remoteAddress, msg);
    assertNotNull(result);
    // Further assert specific fields based on type
}
```

### Example (Incorrect)
```java
// Incorrect: Only tests with a single type (e.g., String), missing the numeric type case
@Test
void testDecode() {
    String msg = "...ABC123...";   // only string type
    Object result = decoder.decode(channel, remoteAddress, msg);
    assertNotNull(result);
}
// This test would not catch the bug because it never exercises the problematic type path.
```