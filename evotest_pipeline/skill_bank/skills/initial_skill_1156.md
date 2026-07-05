---
name: protocol-decoder-type-validation
description: When writing tests for protocol decoders or frame builders, verify that
  all method parameters are properly validated, especially when accepting numeric
  or enum-like arguments. This skill helps catch bugs where type conversion or validation
  is missing for critical parameters that could cause incorrect object construction
  or NullPointerException.
code_tags:
- VALIDATION
- ARGUMENT_VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-type-validation

## Instructions

# Protocol Decoder Parameter Type Validation

## Instructions

- WHEN the TG encounters a protocol decoder or frame builder class that accepts parameters (such as numeric IDs, protocol types, or enum-like values) to construct objects
  - THEN it should test with both valid and invalid parameter values that match the domain of the parameter (e.g., different numeric types, empty values, boundary values)
- WHEN the decoder/factory method appears to parse or convert a parameter but the code does not explicitly validate the parameter's type or range
  - THEN the TG should write a test that passes a suspicious or out-of-range value and verify that the decoder either (a) returns a correct/default/fallback value, or (b) throws an appropriate exception rather than producing a silently incorrect result or NullPointerException
- WHEN the bug fix shows that a simple type conversion method (e.g., `Integer.parseInt`, `Long.parseLong`, or accessing a map/Dictionary with a default fallback) was added
  - THEN the TG should include tests that exercise that conversion path with values that would have previously broken the code (e.g., passing an empty string, a non-numeric string, or a value that triggers the fallback)
- Common pitfalls to avoid:
  - Testing only one type of parameter value (e.g., only String when the protocol also accepts numeric types or references)
  - Assuming that all protocol parameters are properly validated if they pass a single "happy path" test
  - Writing tests that only check happy-path behavior without verifying that invalid inputs are handled correctly
  - Not testing the specific conversion/validation method that was added in the fix

### Example (Correct approach — catches the bug):
```java
// Given a protocol decoder that previously accepted only String type parameters
// but now should also handle numeric types properly:
@Test
public void testDecodeWithNumericType() {
    // Setup decoder with a numeric parameter type
    ProtocolDecoder decoder = new SomeProtocolDecoder();
    // Test with a value that would have caused the bug (e.g., missing type parsing)
    Object result = decoder.decode(someBuffer, someMsg);
    // Verify the result is not null and has expected properties
    assertNotNull(result);
    // Further assertions about the decoded object
}
```

### Example (Incorrect approach — misses the bug):
```java
@Test
public void testDecodeSuccess() {
    // Only tests the happy path with the default/expected parameter type
    // This would NOT catch the bug where a different parameter type breaks decoding
    ProtocolDecoder decoder = new SomeProtocolDecoder();
    Object result = decoder.decode(someBuffer, someMsg);
    assertNotNull(result);
}
```