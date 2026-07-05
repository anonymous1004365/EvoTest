---
name: alternative-protocol-decoding-validation
description: When a protocol decoder has alternative decoding paths (e.g., fallback
  parsing), the TG should test edge cases where type conversion or parsing fails,
  ensuring proper exception handling and validation of alternative paths.
code_tags:
- ARGUMENT_VALIDATION
- TYPE_CONVERSION
test_pattern: EXCEPTION_TEST
---

# alternative-protocol-decoding-validation

## Instructions

# Alternative Protocol Decoding Validation

## Instructions

- WHEN the TG encounters a protocol decoder (e.g., `Gps056ProtocolDecoder`) that performs alternative decoding (e.g., trying one parsing approach and falling back to another), THEN the TG should test that each alternative path correctly handles edge case input data.
  
- WHEN the decoder attempts type conversions such as converting a hex string to an integer using methods like `Integer.parseInt()` or `Long.parseLong()`, THEN the TG should write tests that provide invalid or unexpected string values for those conversions to verify proper exception handling.

- WHEN a decoding step parses a value from a protocol message, THEN the TG should test with both valid and invalid/malformed protocol data to ensure:
  1. The expected decoded output is produced for valid inputs
  2. The decoder does not throw an unexpected exception for malformed inputs
  3. The decoder handles edge cases like empty strings, null values, or out-of-range numeric values

- Common pitfalls to avoid:
  - Testing only the "happy path" with valid protocol messages
  - Assuming type conversions will always succeed without verifying the behavior when they fail
  - Not testing boundary values for numeric fields (e.g., zero, maximum values, negative values for unsigned fields)
  - Forgetting that alternative decoding paths may handle exceptions differently and one path may succeed where another fails

### Correct Example

```java
@Test
public void testDecodeWithInvalidFieldValue() {
    // Create a protocol message with an invalid hex value in a field
    // that would trigger a NumberFormatException if parsed incorrectly
    String invalidMessage = "*HQ,1234567890,V1,1234,ABCXYZ#"; // ABCXYZ is not a valid hex
    assertThrows(...); // Verify the decoder handles this gracefully
}
```

### Incorrect Example

```java
@Test
public void testDecodeOnlyValid() {
    // Only tests the happy path - misses the bug entirely
    String validMessage = "*HQ,1234567890,V1,1234,1A2B3C#";
    // Test passes but doesn't catch the type conversion bug
}
```