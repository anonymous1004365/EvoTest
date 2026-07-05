---
name: protocol-decoder-alternative-path-parameter-types
description: When a protocol decoder has multiple decoding paths (alternative paths)
  based on parameter types, the TG should test with each distinct type to ensure all
  paths are reachable and correctly handled.
code_tags:
- ALTERNATIVE_PROTOCOL_DECODING
- ARGUMENT_VALIDATION
- EXCEPTION_HANDLING
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-alternative-path-parameter-types

## Instructions

# Protocol Decoder Alternative Path Parameter Types

## Instructions

- WHEN the TG encounters a protocol decoder (like `ArknavProtocolDecoder`) that processes different parameter types (e.g., `String` vs `CtTypeReference`) through alternative decoding paths
- THEN the TG should write separate test cases for each distinct parameter type that triggers a different code path:
  1. Identify all distinct types the decoder can receive (e.g., `String` vs `CtTypeReference` for template parameters)
  2. Create one test input per type per decoding scenario
  3. Verify each test passes on the fixed version and fails (throws an appropriate exception like `IndexOutOfBoundsException`, `NullPointerException`, or returns incorrect/unexpected result) on the buggy version
  4. Pay attention to parsing/manipulation logic that may treat different types differently (e.g., accessing characters by index, splitting strings, type casting, iterator traversal)
- Common pitfalls:
  - Testing ONLY one parameter type (e.g., only `String`) when the decoder accepts multiple types — this misses bugs triggered by the alternative path
  - Assuming all parameter types go through the same logic — check for type-specific branches (type checks, `instanceof`, casting)
  - Not verifying the actual decoded output value, only checking that no exception is thrown
  - Ignoring edge cases like empty strings, null values, or boundary indices in string/collection manipulations within alternative decoding paths

### Correct Example (conceptual)
```java
// Test with String type parameter
@Test 
public void testDecodeWithStringParam() {
    // Create decoder, send a message with String-type parameter
    // Buggy version might cause IndexOutOfBoundsException on character access
    // Fixed version should return the correctly decoded object
    Object result = decoder.decode(channel, remoteAddress, msg);
    assertNotNull(result);
    // verify specific decoded fields
}

// Test with CtTypeReference type parameter (alternative path)
@Test
public void testDecodeWithCtTypeRefParam() {
    // Create decoder, send a message with CtTypeReference-type parameter
    // Buggy version might fail on iterator handling or type-specific manipulation
    Object result = decoder.decode(channel, remoteAddress, msg);
    assertNotNull(result);
    // verify specific decoded fields
}
```

### Incorrect Example
```java
// WRONG: Only testing one parameter type misses the alternative path bug
@Test
public void testDecodeOnly() {
    // Only tests with String-type parameter
    // If the bug only manifests with CtTypeReference parameters, this test passes on both versions
    Object result = decoder.decode(channel, remoteAddress, msg);
    assertNotNull(result);
}
```