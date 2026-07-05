---
name: trackbox-protocol-decoder-input-validation
description: When decoding protocol frames with alternative parsing paths, test that
  invalid or unexpected input values (like negative numbers) do not cause silent failures
  or incorrect field extractions. This skill helps write tests that expose missing
  parameter validation in protocol decoders.
code_tags:
- ARGUMENT_VALIDATION
- VALIDATION
- NULL_CHECK
test_pattern: EXCEPTION_TEST
---

# trackbox-protocol-decoder-input-validation

## Instructions

# Trackbox Protocol Decoder Input Validation

## Instructions

- WHEN the TG encounters a protocol decoder class (like `TrackboxProtocolDecoder`) that parses binary or string-encoded data into fields (e.g., speed, course, power, distance), especially when the decoder has a primary parsing path and an alternative/fallback parsing path for different message formats
- THEN the TG should write tests that supply **invalid, out-of-range, or unexpected values** for numeric fields (e.g., negative speed, negative course, negative power, negative distance) and verify that:
  - The decoder either **rejects** the input (throws an exception like `IllegalArgumentException` or `RuntimeException`)
  - OR handles the values **consistently** between the parsing paths (the same input yields the same result regardless of which path is taken)
  - Specific fields to test include: speed (e.g., -1, -0.5), course (e.g., -1, 360, 361), power (e.g., -1, -10), distance (e.g., -1, -100), RPM (e.g., -1)
- Common pitfalls to avoid:
  - **Testing only on the happy path**: Do NOT assume that just because one parsing path works, the alternative path handles edge cases equally. Test each parsing path separately.
  - **Assuming negative values are impossible**: Even if the protocol "shouldn't" send negative values, a decoder must handle them gracefully. Write tests that explicitly pass negative values.
  - **Ignoring field-by-field validation**: Do NOT test only the overall message structure. Test that each individual numeric field is properly validated or correctly extracted.
  - **Missing boundary values**: Test boundary values (0, negative values just below 0, max values) for numeric fields, not just typical values.

### Correct Example (what to do)

```java
@Test
public void testDecodeWithNegativeSpeed() {
    TrackboxProtocolDecoder decoder = new TrackboxProtocolDecoder();
    // Construct a message with negative speed value
    String invalidMsg = "..."; // message with speed = -1
    // Expect the decoder to either throw or produce a position with speed = 0 or -1
    // Verify the behavior is consistent
    Position position = decoder.decode(null, null, invalidMsg);
    assertNotNull("Position should still be decoded", position);
    // Check that speed is handled (either 0 or original negative, but not silently swapped)
}
```

### Incorrect Example (what to avoid)

```java
@Test
public void testDecodeHappyPath() {
    TrackboxProtocolDecoder decoder = new TrackboxProtocolDecoder();
    // Only testing normal positive values, missing edge cases
    String validMsg = "..."; // message with speed = 10
    Position position = decoder.decode(null, null, validMsg);
    assertEquals(10.0, position.getSpeed(), 0.01);
    // Buggy alternative path might handle negative speeds incorrectly,
    // but this test never checks that case
}
```