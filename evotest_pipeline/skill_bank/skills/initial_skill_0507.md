---
name: protocol-message-parser-edge-cases
description: When decoding protocol messages (like GPS/telemetry data), test with
  both String and type-specific parameters for message data fields. This skill helps
  detect parsing failures when the decoder incorrectly handles non-default parameter
  types.
code_tags:
- NULL_CHECK
- TYPE_CONVERSION
- VALIDATION
test_pattern: EXCEPTION_TEST
---

# protocol-message-parser-edge-cases

## Instructions

# Protocol Message Parser Edge Case Testing

## Instructions

- WHEN the TG encounters a message decoder or protocol parser class (e.g., `H02ProtocolDecoder`) that processes positional or telemetry data (latitude, longitude, speed, course, etc.)
- THEN the TG should write tests that:
  - Call the decode method with both `String` arguments AND arguments of other relevant types (e.g., `CtTypeReference`, `Integer`, etc.) for parameters like template arguments or message fields
  - Verify that the decode operation does not throw a `NullPointerException` or `ClassCastException` when non-String types are passed
  - For positional data, test with edge values (e.g., zero coordinates, boundary values like -90/90 for latitude, -180/180 for longitude)
  
- Common pitfalls to avoid:
  - Testing only with valid String-type parameters and assuming other types will work the same way
  - Forgetting to test null values for optional message fields (e.g., speed, course, satellite count)
  - Not testing empty strings or blank strings where protocol fields may be parsed
  - Assuming all parameters to `decode()` or similar parsing methods are always the same type as the template parameter

- Correct example:
```java
@Test
public void testDecodeWithMixedParameterTypes() throws Exception {
    H02ProtocolDecoder decoder = new H02ProtocolDecoder();
    // Test with String type parameter
    decoder.decode(null, null, "some data");
    // Also test with other parameter types that may be passed at runtime
    decoder.decode(null, null, someCtTypeReference); // e.g., when used as template proxy
}
```

- Incorrect example (too narrow):
```java
@Test
public void testDecode() throws Exception {
    // Only testing with String - misses the type conversion bug
    H02ProtocolDecoder decoder = new H02ProtocolDecoder();
    decoder.decode(null, null, "test data");
}
```