---
name: protocol-decoder-subclass-variants
description: When testing protocol decoders that use alternative or conditional decoding
  paths for different frame types, test each distinct codec variant (subclass or alternative
  path) to ensure they all handle the same input correctly. The bug involves a decoder
  having an alternative frame decoder that processes data differently than the primary
  path, and the test only exercises one path.
code_tags:
- ARGUMENT_VALIDATION
- NULL_CHECK
- VALIDATION
- TYPE_CONVERSION
test_pattern: PARAMETRIC_TEST
---

# protocol-decoder-subclass-variants

## Instructions

# Protocol Decoder Subclass/Variant Coverage

## Instructions

**WHEN** the TG encounters a protocol decoder class (such as `SuntechProtocolDecoder`) that may use an alternative or conditional decoding path (e.g., a separate frame decoder like `SuntechFrameDecoder`), or there are multiple subclasses/variants of the decoder:

- **THEN** the TG should verify that all distinct decoding paths/variants are exercised in the test. Do not assume that testing with one message type covers all code paths.
- **THEN** the TG should create a parametrized test (using `@ParameterizedTest` and `@CsvSource` or `@MethodSource`) that provides at least one representative input for each distinct frame type or decoder variant that the class can handle.
- **THEN** the TG should verify that for each variant, the decoded position data (e.g., latitude, longitude, speed, course) is non-null and within expected ranges (e.g., latitude between -90 and 90, longitude between -180 and 180).
- **THEN** the TG should include test cases where the input format differs significantly (e.g., different field orders, additional fields, or different checksum formats) if the protocol specification allows such variants.

**Common pitfalls to avoid:**
- Writing a test that only exercises the most common or first-found decoding path and assuming all messages will be handled identically.
- Failing to test edge cases where the alternative decoder might incorrectly interpret data (e.g., swapping latitude/longitude, misreading checksums, or returning null for valid messages).
- Using a single sample message to cover multiple decoder branches without verifying which branch was actually taken.
- Not checking for `NullPointerException` or `IndexOutOfBoundsException` when the alternative decoder receives data in a format it doesn't expect.

**Example (correct) — parametrized test covering multiple variants:**

```java
@ParameterizedTest
@CsvSource({
    // Primary decoder variant: standard position report
    "123456789012345,1,2021-01-01 12:00:00,40.7128,-74.0060,0,0,0,0,0",
    // Alternative decoder variant: additional fields present (e.g., extra status byte)
    "123456789012345,2,2021-01-01 12:00:00,40.7128,-74.0060,0,0,0,0,0,EXTRA",
    // Minimal variant: fewer fields, using defaults for missing values
    "123456789012345,1,2021-01-01 12:00:00,40.7128,-74.0060"
})
void testDecodeWithVariant(String id, int type, String date, double lat, double lon, 
                           double speed, double course, int status, int battery, int ... extra) {
    SuntechProtocolDecoder decoder = new SuntechProtocolDecoder(null);
    // ... construct message and verify decoded position
}
```

**Example (incorrect) — testing only one variant:**

```java
// BUG: Only tests one decoding path. If the alternative path has a different
// message format (e.g., swapped lat/lon, different date format), the bug is missed.
@Test
void testDecode() {
    SuntechProtocolDecoder decoder = new SuntechProtocolDecoder(null);
    String msg = "123456789012345,1,2021-01-01 12:00:00,40.7128,-74.0060,0,0";
    Position position = decoder.decode(null, null, msg);
    assertNotNull(position);
    assertEquals(40.7128, position.getLatitude(), 0.0001);
}
```